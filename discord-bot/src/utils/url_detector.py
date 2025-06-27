import re
from typing import List
from config import Config

class URLDetector:
    """Detects and validates video URLs from various platforms."""
    
    def __init__(self):
        # URL patterns for different platforms
        self.patterns = {
            'youtube': [
                r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
                r'https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
                r'https?://youtu\.be/[\w-]+',
                r'https?://(?:m\.)?youtube\.com/watch\?v=[\w-]+',
            ],
            'instagram': [
                r'https?://(?:www\.)?instagram\.com/reel/[\w-]+',
                r'https?://(?:www\.)?instagram\.com/p/[\w-]+',
                r'https?://(?:www\.)?instagram\.com/tv/[\w-]+',
            ]
        }
        
        # Compile all patterns
        self.compiled_patterns = {}
        for platform, patterns in self.patterns.items():
            self.compiled_patterns[platform] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def extract_video_urls(self, text: str) -> List[str]:
        """
        Extract video URLs from text.
        
        Args:
            text: Text to search for URLs
            
        Returns:
            List of valid video URLs found in the text
        """
        found_urls = []
        
        # General URL pattern to find all URLs first
        url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+', re.IGNORECASE)
        potential_urls = url_pattern.findall(text)
        
        for url in potential_urls:
            # Clean up URL (remove trailing punctuation)
            cleaned_url = self._clean_url(url)
            
            # Check if it's a supported video URL
            if self._is_video_url(cleaned_url):
                found_urls.append(cleaned_url)
        
        return found_urls
    
    def _clean_url(self, url: str) -> str:
        """Clean up URL by removing trailing punctuation and parameters."""
        # Remove trailing punctuation that might be part of sentence
        url = re.sub(r'[.,;!?]+$', '', url)
        
        # For some platforms, we might want to clean up tracking parameters
        # This is optional and can be customized based on needs
        
        return url
    
    def _is_video_url(self, url: str) -> bool:
        """
        Check if URL is a supported video URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from a supported platform and enabled
        """
        for platform, patterns in self.compiled_patterns.items():
            # Check if platform is enabled
            if not Config.SUPPORTED_PLATFORMS.get(platform, False):
                continue
            
            # Check if URL matches any pattern for this platform
            for pattern in patterns:
                if pattern.match(url):
                    return True
        
        return False
    
    def get_platform(self, url: str) -> str:
        """
        Determine which platform a URL belongs to.
        
        Args:
            url: URL to check
            
        Returns:
            Platform name or 'unknown'
        """
        for platform, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.match(url):
                    return platform
        
        return 'unknown'
    
    def is_supported_platform(self, platform: str) -> bool:
        """
        Check if a platform is supported and enabled.
        
        Args:
            platform: Platform name to check
            
        Returns:
            True if platform is supported and enabled
        """
        return Config.SUPPORTED_PLATFORMS.get(platform, False)
    
    def validate_url(self, url: str) -> bool:
        """
        Validate a single URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and supported
        """
        return self._is_video_url(url)
