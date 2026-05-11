### Custom kernel for RM6785 devices
Stormbreaker Kernel for Realme 6, 6i, 6s and Narzo

- **`main` branch:**
  - Default unmodified branch
  - Nothing included
- **`ksu_next` branch:**
  - KernelSU-Next setup script & automated hook setup script
  - Droidspace patch & configuration files
- **`resukisu` branch:**
  - ReSukiSU setup script
  - Droidspace patch & configuration files

> [!NOTE]
> SuSFS is not inlcuded
> 
> `path_umount` is not included in `ksu_next` branch. 
> 
> Due to fragmentation of automated hooks script, ksu hooks are already included in kernel source files in `resukisu` branch.
>
> Add `CONFIG_KSU=y` and `CONFIG_KSU_MANUAL_HOOK=y` inside defconfig. Also if you ever run `make mrproper`, it will say that KSU hooks are not integrated, ignore it

For flashable `.zip`s checkout [Release](https://github.com/Prime-TITAN-CameraMan/android_kernel_realme_nemo/releases). And carefully read everything there before flashing the zip
