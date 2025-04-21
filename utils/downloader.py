import os
import re
import aiohttp
import tempfile
import asyncio
from urllib.parse import urlparse

class TeraboxDownloader:
    """
    Utility class to download videos from Terabox.
    """

    @staticmethod
    def is_valid_terabox_url(url):
        """
        Check if provided URL is a valid Terabox URL
        """
        parsed = urlparse(url)
        return bool(
            re.match(
                r"^(www\.)?(terabox\.com|teraboxapp\.com|1024tera\.com|4funbox\.com)$",
                parsed.netloc
            )
        )

    @staticmethod
    async def _get_direct_download_link(url):
        """
        Get the direct download link from a Terabox URL
        Using the Terabox API
        """
        TERABOX_API = "https://api.terabox.app/api/get-download"

        # Clean the URL
        url = url.strip()

        async with aiohttp.ClientSession() as session:
            try:
                # Get download link from API
                params = {"url": url}
                async with session.get(TERABOX_API, params=params) as response:
                    if response.status != 200:
                        return None

                    data = await response.json()
                    if data.get("status") != "success":
                        return None

                    # Return direct download link
                    return data.get("data", {}).get("direct_link")

            except Exception as e:
                print(f"Error getting direct download link: {e}")
                return None

    @staticmethod
    async def download_video(url, progress_callback=None):
        """
        Download a video from Terabox URL

        Args:
            url: Terabox URL
            progress_callback: Optional callback function to report progress

        Returns:
            path to downloaded file or None if download failed
        """
        if not TeraboxDownloader.is_valid_terabox_url(url):
            return None, "Invalid Terabox URL"

        # Get direct download link
        direct_link = await TeraboxDownloader._get_direct_download_link(url)
        if not direct_link:
            return None, "Failed to get direct download link"

        # Create a temporary file to download to
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_file.close()

        try:
            # Download the file
            async with aiohttp.ClientSession() as session:
                async with session.get(direct_link, timeout=60*10) as response:  # 10 min timeout
                    if response.status != 200:
                        os.unlink(temp_file.name)
                        return None, f"Download failed with status {response.status}"

                    # Get total size if available
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded_size = 0

                    with open(temp_file.name, 'wb') as fd:
                        chunk_size = 1024 * 1024  # 1MB chunks

                        async for chunk in response.content.iter_chunked(chunk_size):
                            fd.write(chunk)
                            downloaded_size += len(chunk)

                            # Report progress
                            if progress_callback and total_size:
                                progress = (downloaded_size / total_size) * 100
                                await progress_callback(progress)

            return temp_file.name, None

        except asyncio.TimeoutError:
            os.unlink(temp_file.name)
            return None, "Download timed out"
        except Exception as e:
            os.unlink(temp_file.name)
            return None, f"Download error: {str(e)}"
