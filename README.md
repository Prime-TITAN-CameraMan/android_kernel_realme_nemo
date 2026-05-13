### Custom kernel for RM6785 devices
Stormbreaker Kernel for Realme 6, 6i, 6s and Narzo

- **`main` branch:**
  - Default untouched branch
  - Nothing included
- **`ksu_next` branch:**
  - KernelSU-Next setup script & integrated hooks in the source files
  - Droidspace configuration files
- **`resukisu` branch:**
  - ReSukiSU setup script & integrated hooks in the source files
  - Droidspace configuration files

> [!NOTE]
> SuSFS is not inlcuded
> 
> `path_umount` is backported to both `ksu_next` branch & `resukisu` branch
> 
> KSU hooks are already included in source files of `ksu_next` branch & `resukisu` branch, no need to integration

For flashable `.zip`s checkout [Release](https://github.com/Prime-TITAN-CameraMan/android_kernel_realme_nemo/releases). And carefully read everything there before flashing the zip
