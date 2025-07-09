import os
import subprocess
import shutil
from git import Repo  # pip install gitpython
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


def install_android_sdk():
    """Installs the Android SDK command line tools and necessary packages.
    This function downloads the command line tools, extracts them, and installs the required SDK packages.
    It assumes that the user has wget and unzip installed on their system.
    """
    # Define path where SDK will be installed
    sdk_path = os.path.expanduser("~/android-sdk")
    cmdline_tools_url = os.getenv("CMDLINE_TOOLS_URL")
    sdkmanager = os.path.join(
        sdk_path, "cmdline-tools", "cmdline-tools", "bin", "sdkmanager"
    )
    # Verify if the sdkmanager already exists (SDK installed)
    if os.path.exists(sdkmanager):
        print("Android SDK is already installed. No action needed.")
        return
    # Download and extract command line tools
    try:
        subprocess.run(
            ["wget", cmdline_tools_url, "-O", "cmdline-tools.zip"], check=True
        )
        subprocess.run(["mkdir", "-p", f"{sdk_path}/cmdline-tools"], check=True)
        subprocess.run(
            ["unzip", "cmdline-tools.zip", "-d", f"{sdk_path}/cmdline-tools"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error downloading or extracting command line tools: {e}")
        raise e
    # Install necessary SDK packages
    try:
        sdkmanager = f"{sdk_path}/cmdline-tools/cmdline-tools/bin/sdkmanager"
        sdkplatforms = os.getenv("ANDROID_SDK_PLATFORMS")
        sdkbuildtools = os.getenv("ANDROID_BUILD_TOOLS")

        subprocess.run(f"yes | {sdkmanager} --licenses", shell=True, check=True)
        subprocess.run(
            [
                sdkmanager,
                "--sdk_root=" + sdk_path,
                "platform-tools",
                f"platforms;{sdkplatforms}",
                f"build-tools;{sdkbuildtools}",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error installing SDK packages: {e}")
        raise e
    # Clean up downloaded zip file
    if os.path.exists("cmdline-tools.zip"):
        os.remove("cmdline-tools.zip")
    else:
        print("cmdline-tools.zip not found, nothing to remove.")


def clone_repository():
    """Clones a specified Android project repository from GitHub.
    This function uses GitPython to clone the repository into a temporary directory.
    """
    repo_url = os.getenv("REPO_URL")
    dest_dir = os.getenv("PROJECT_DIR")

    try:
        Repo.clone_from(repo_url, dest_dir)
    except Exception as e:
        print(f"Error cloning repository: {e}")
        raise e


def clone_repo():
    """Clones a specified Android project repository from GitHub.
    This function uses subprocess to run the git clone command.
    """
    repo_url = os.getenv("REPO_URL")
    dest_dir = os.getenv("PROJECT_DIR")

    try:
        subprocess.run(["git", "clone", repo_url, dest_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        raise e


def create_local_properties():
    """Create local.properties file with the SDK path."""
    project_dir = os.getenv("PROJECT_DIR")
    sdk_path = os.path.expanduser(os.getenv("ANDROID_SDK_HOME"))

    local_properties_path = os.path.join(project_dir, "local.properties")
    with open(local_properties_path, "w") as f:
        f.write(f"sdk.dir={sdk_path}\n")


def generate_apk():
    """Generates an APK from the cloned Android project.
    This function assumes that the project uses Gradle as its build system.
    It changes the working directory to the project directory and runs the Gradle build command.
    """
    try:
        project_dir = os.getenv("PROJECT_DIR")
        os.chdir(project_dir)
        subprocess.run(["chmod", "+x", "./gradlew"], check=True)
        subprocess.run(["./gradlew", "assembleDebug"], check=True)

        apk_path = os.path.join(
            project_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk"
        )
        output_dir = os.getenv("OUTPUT_DIR")
        os.makedirs(output_dir, exist_ok=True)
        apk_name = os.getenv("APK_NAME")
        new_apk_path = os.path.join(output_dir, apk_name)
        shutil.move(apk_path, new_apk_path)
        print(f"APK moved to: {new_apk_path}")
        print("APK generation completed successfully.")
        print(f"You can find the generated APK in the '{new_apk_path}' directory.")
    except subprocess.CalledProcessError as e:
        print(f"Error during APK generation: {e}")
        raise e


def delete_project_dir():
    """Remove the project's directory and all its contents."""
    project_dir = os.getenv("PROJECT_DIR")
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
        print(f"'{project_dir}' removed successfully.")
        print("Project directory cleaned up.")
    else:
        print(f"Directory '{project_dir}' not found.")


if __name__ == "__main__":
    print("Make sure to have the necessary permissions to run this script.")
    install_android_sdk()
    clone_repository()
    create_local_properties()
    generate_apk()
    delete_project_dir()
    print(
        "Run the script again to generate a new APK or clean up the project directory."
    )
