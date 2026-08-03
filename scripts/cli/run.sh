#!/usr/bin/env bash

set -e

VM_DIR="vm"
DISK="$VM_DIR/ChurrOS.qcow2"
VARS="$VM_DIR/OVMF_VARS.fd"

ISO=$(find out -name "*.iso" | head -n1)

FORCE_NOKVM=false
for arg in "$@"; do
    case "$arg" in
        --nokvm) FORCE_NOKVM=true ;;
    esac
done

if [ -z "$ISO" ]; then
    echo "No ISO found."
    echo "Building..."

    ./churros build

    ISO=$(find out -name "*.iso" | head -n1)
fi

mkdir -p "$VM_DIR"

if [ ! -f "$DISK" ]; then
    echo
    echo "Creating development virtual machine..."
    echo

    qemu-img create -f qcow2 "$DISK" 64G
fi

if [ ! -f "$VARS" ]; then
    cp /usr/share/edk2/x64/OVMF_VARS.4m.fd "$VARS"
fi

echo
echo "Launching ChurrOS Development VM..."
echo

KVM_ARGS=""
GPU_ARGS=""
CPU_ARGS=""

if [ "$FORCE_NOKVM" = false ] && [ -e /dev/kvm ] && [ -r /dev/kvm ] && [ -w /dev/kvm ]; then
    echo "  KVM acceleration: enabled"
    KVM_ARGS="-cpu host"
    CPU_ARGS="-smp 4"
    MACHINE_ARGS="-machine q35,accel=kvm"
else
    echo "  KVM acceleration: not available (using software emulation)"
    KVM_ARGS=""
    CPU_ARGS="-smp 2"
    MACHINE_ARGS="-machine q35"
fi

# niri requires hardware-accelerated 3D (OpenGL via virgl).
# Always attempt virtio-gpu-gl with GL; fall back to virtio-gpu (no GL) only if
# the host lacks /dev/dri entirely — in that case niri will try llvmpipe.
if [ -e /dev/dri ]; then
    GPU_ARGS="-device virtio-vga-gl -display gtk,gl=on"
    echo "  GPU: virtio-vga-gl + virgl (3D)"
else
    GPU_ARGS="-device virtio-gpu -display gtk,gl=off"
    echo "  GPU: virtio-gpu (no 3D — niri may fall back to software rendering)"
fi

qemu-system-x86_64 \
    $MACHINE_ARGS \
    $KVM_ARGS \
    $CPU_ARGS \
    -m 4096 \
    $GPU_ARGS \
    -device qemu-xhci \
    -device usb-tablet \
    -device intel-hda \
    -device hda-duplex \
    -drive if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd \
    -drive if=pflash,format=raw,file="$VARS" \
    -drive file="$DISK",format=qcow2,if=virtio \
    -cdrom "$ISO" \
    -boot order=d \
    -serial file:vm_serial.log
