from sys import platform
import zipfile
from requests import get
from os import listdir, rename, mkdir, environ
from os.path import abspath, join, isfile, isdir
from subprocess import run

zip_path = "commandlinetools.zip"

android_dir = abspath(join(".android"))
cmdline_path = join(android_dir, "cmdline-tools")
platform_path = join(android_dir, "platforms")

download_url = {
    "win32":
    "https://dl.google.com/android/repository/commandlinetools-win-9477386_latest.zip",
    "linux":
    "https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip",
    "darwin":
    "https://dl.google.com/android/repository/commandlinetools-mac-9477386_latest.zip"
}


def ensure_zip():
    if not isfile(join(zip_path)):
        print("Command line tools are not present, downloading")
        with open(zip_path, "wb") as clt:
            clt.write(get(download_url[platform]).content)
            clt.flush()


def ensure_android():
    if not isdir(join(cmdline_path)):
        ensure_zip()
        print("Android directory is not present, extracting.")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(cmdline_path)
        rename(join(cmdline_path, "cmdline-tools"),
               join(cmdline_path, "latest"))
    else:
        print("Android directory already exists, skipping.")


ensure_android()

if not isdir(platform_path):
    mkdir(platform_path)

environ["ANDROID_SDK_ROOT"] = android_dir

bin_path = join(cmdline_path, "latest", "bin")
bins = listdir(bin_path)
emulator_path = join(android_dir, "emulator")
emulator_bins = listdir(emulator_path)

avd_manager_path = join(bin_path,
                        [bin for bin in bins
                         if bin.startswith("avdmanager")][0])
sdk_manager_path = join(bin_path,
                        [bin for bin in bins
                         if bin.startswith("sdkmanager")][0])

emulator_path = join(emulator_path, [
    bin for bin in emulator_bins
    if bin.startswith("emulator") and ("-" not in bin)
][0])

print(avd_manager_path)
print(sdk_manager_path)
print(emulator_path)

run([sdk_manager_path, "--install", "platform-tools"])
run([sdk_manager_path, "--install", "build-tools;32.0.0"])
run([
    sdk_manager_path, "--install",
    "system-images;android-32;google_apis_playstore;x86_64"
])
run([
    avd_manager_path, "create", "avd", "--name", "Machine1", "--device", "28",
    "--package", "system-images;android-32;google_apis_playstore;x86_64"
])

run([emulator_path, "-avd", "Machine1"])