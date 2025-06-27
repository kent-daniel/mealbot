import pytest
from utils.url_detector import URLDetector


class TestURLDetector:
    """Test cases for URL detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = URLDetector()
    
    def test_youtube_url_detection(self):
        """Test YouTube URL detection."""
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtube.com/shorts/abc123",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in test_urls:
            urls = self.detector.extract_video_urls(url)
            assert len(urls) == 1
            assert urls[0] == url
            assert self.detector.get_platform(url) == 'youtube'
    
    def test_instagram_url_detection(self):
        """Test Instagram URL detection."""
        test_urls = [
            "https://www.instagram.com/reel/ABC123/",
            "https://instagram.com/p/DEF456/",
            "https://www.instagram.com/tv/GHI789/"
        ]
        
        for url in test_urls:
            urls = self.detector.extract_video_urls(url)
            assert len(urls) == 1
            assert urls[0] == url
            assert self.detector.get_platform(url) == 'instagram'
    
    def test_tiktok_url_detection(self):
        """Test TikTok URL detection."""
        test_urls = [
            "https://www.tiktok.com/@user/video/1234567890",
            "https://vm.tiktok.com/ABC123/",
            "https://tiktok.com/t/DEF456/"
        ]
        
        for url in test_urls:
            urls = self.detector.extract_video_urls(url)
            assert len(urls) == 1
            assert urls[0] == url
            assert self.detector.get_platform(url) == 'tiktok'
    
    def test_multiple_urls_in_text(self):
        """Test detection of multiple URLs in text."""
        text = """
        Check out these recipes:
        https://www.youtube.com/watch?v=dQw4w9WgXcQ
        and this one: https://instagram.com/reel/ABC123/
        Also: https://tiktok.com/@user/video/1234567890
        """
        
        urls = self.detector.extract_video_urls(text)
        assert len(urls) == 3
    
    def test_invalid_urls(self):
        """Test that invalid URLs are not detected."""
        invalid_urls = [
            "https://www.google.com",
            "https://facebook.com/video/123",
            "not a url at all",
            "https://youtube.com/invalid",
            ""
        ]
        
        for url in invalid_urls:
            urls = self.detector.extract_video_urls(url)
            assert len(urls) == 0
    
    def test_url_cleaning(self):
        """Test URL cleaning functionality."""
        dirty_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ."
        clean_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        urls = self.detector.extract_video_urls(dirty_url)
        assert len(urls) == 1
        assert urls[0] == clean_url
    
    def test_platform_validation(self):
        """Test platform validation."""
        assert self.detector.is_supported_platform('youtube') == True
        assert self.detector.is_supported_platform('instagram') == True
        assert self.detector.is_supported_platform('tiktok') == True
        assert self.detector.is_supported_platform('unknown') == False
    
    def test_url_validation(self):
        """Test URL validation."""
        valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        invalid_url = "https://www.google.com"
        
        assert self.detector.validate_url(valid_url) == True
        assert self.detector.validate_url(invalid_url) == False
