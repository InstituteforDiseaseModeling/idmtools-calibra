import hashlib
import os
import stat
from pathlib import Path
from sys import exit
from enum import Enum
from getpass import getpass
from logging import getLogger
import requests
import emodpy.bamboo_api_utils as bamboo_api
from idmtools.utils.decorators import optional_yaspin_load

# Github URLs
ERADICATION_GIT_URL_TEMPLATE = 'https://github.com/InstituteforDiseaseModeling/EMOD/releases/download/v{}/Eradication{}'

logger = getLogger(__name__)


class EradicationPlatformExtension(Enum):
    LINUX = ''
    Windows = '.exe'


class EradicationBambooBuilds(Enum):
    BETA_COVID = 'DTKGOCT-SCONSWINENVSFT'
    CI_GENERIC = 'DTKGENCI-SCONSWINGEN'
    CI_MALARIA = 'DTKMALCI-SCONSWINMAL'
    CI_HIV = 'DTKHIVCI-RELWINHIV'
    GENERIC = 'DTKGEN-DTKRELLNX'
    DENGUE = 'DTKACTDENGUE-DTKACTDENGUERELLNX',
    ENVIRONMENTAL = 'DTKACTIVETFBRANCH-SCONSWINENV'
    EMOD_RELEASE = 'EMODREL-SCONSRELLNX'
    FP = 'DTKFP-SCONSRELLNX'
    HIV = 'DTKHIVONGOING-HIVOGSCONSRELNX'
    MALARIA = 'DTKACTIVEMALBRANCH-DTKACTMALRELLNX'
    RELEASE = 'DTKREL-SCONSRELLNX'
    TBHIV = 'DTKACTTBHIV-SCONSLNXALL'
    TYPHOD = 'DTKACTIVETFBRANCH-DTKACTTFRELLNXTF'
    GENERIC_WIN = 'DTKGENCI-SCONSWINGEN'
    CI_GENERICLINUX = 'DTKMASTERCI-SCONSRELLNX'


def get_github_eradication_url(version: str,
                               extension: EradicationPlatformExtension = EradicationPlatformExtension.LINUX) -> str:
    """
    Get the github eradication url for specified release

    Args:
        version: Release to fetch
        extension: Optional extensions. Defaults to Linux(None)
    Returns:
        Url of eradication release
    """

    return ERADICATION_GIT_URL_TEMPLATE.format(version, extension.value)


def save_bamboo_credentials(username, password):
    """Save bamboo api login credentials using keyring.

    Args:
        username (str): bamboo api login username (e.g. somebody@idmod.org)
        password (str): bamboo api login password
    """
    bamboo_api.save_credentials(username, password)


def bamboo_api_login():
    """Automatically login to bamboo, prompt for credentials if none are cached or there's no login session."""
    success = False
    try:
        success = bamboo_api.bamboo_connection().login()
        if success:
            return
    except PermissionError:
        success = False

    retries = 3
    while not success and retries > 0:
        retries += -1
        print('Unable to login to Bamboo API, please provide a username and password.')
        username = input('Username: ')
        password = getpass('Password: ')
        try:
            if username and password:
                success = bamboo_api.bamboo_connection().login(username, password)
                if success:
                    save_pass = input('Login successful, save username and password to keyring? [y/N] ')
                    if save_pass.strip().lower() == 'y':
                        save_bamboo_credentials(username, password)
                        print('Saved.')
                    return
            else:
                print('Username/password cannot be blank.')
        except PermissionError:
            success = False
            print('Permission error logging in to Bamboo API.')

    exit(1)


def download_latest_bamboo(plan: EradicationBambooBuilds, scheduled_builds_only: bool = True,
                           out_path: str = None) -> str:  # noqa F821
    """
    Downloads the latest successful build for an Eradication Bamboo Plan to specified path

    Args:
        plan: Bamboo Plan key. for supported build
        out_path: Output path to save file (default to current directory)

    Returns:
        Returns list of downloaded files on filesystem
    """
    bamboo_api_login()
    if not out_path:
        out_path = os.getcwd()

    build_num, build_info = bamboo_api.BuildInfo.get_latest_successful_build(plan.value,
                                                                             scheduled_only=scheduled_builds_only)
    if not build_num:
        raise FileNotFoundError(
            f"Could not find a successful build for plan {plan.value}. Please check plan name again")

    downloaded_files = bamboo_api.BuildArtifacts.download_artifact_to_file(plan.value, build_num, 'Eradication.exe',
                                                                           out_path)
    if len(downloaded_files) >= 1:
        return downloaded_files[0]
    return ''


def download_from_url(url, out_path: str = None) -> str:
    if not out_path:
        out_path = os.getcwd()
    downloaded_file = bamboo_api.BuildArtifacts.download_from_bamboo_url(url, out_path)
    return downloaded_file


@optional_yaspin_load(text='Downloading file')
def download_eradication(url: str, cache_path: str = None, spinner=None):
    """
    Downloads Eradication binary

    Useful for downloading binaries from Bamboo or Github

    Args:
        url: Url to binary
        cache_path: Optional output directory
        spinner: Spinner object

    Returns:
        Full path to output file
    """
    # download eradication from path to our local_data cache
    if cache_path is None:
        cache_path = os.path.join(str(Path.home()), '.local_data', "eradication-cache")
    elif os.path.exists(cache_path) and os.path.isfile(cache_path):
        raise ValueError("Path must be a directory")
    filename = hashlib.md5(url.encode('utf-8')).hexdigest()
    out_name = os.path.join(cache_path, filename)
    os.makedirs(cache_path, exist_ok=True)
    if not os.path.exists(out_name):
        if spinner:
            spinner.text = f"Downloading {url} to {out_name}"
        logger.debug(f"Downloading {url} to {out_name}")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(out_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        # ensure on linux we make it executable locally
        if os.name != 'nt':
            st = os.stat(out_name)
            os.chmod(out_name, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        logger.debug(f"Finished downloading {url}")
    else:
        logger.debug(f'{url} already cached as {out_name}')
    return out_name


ERADICATION_213 = get_github_eradication_url('2.13.0')
ERADICATION_218 = get_github_eradication_url('2.18.0')
ERADICATION_220 = get_github_eradication_url('2.20.0')
