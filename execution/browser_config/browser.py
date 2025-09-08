import sys
import setuptools  # Critical for distutils replacement

class Browser:
    """
    Singleton class to manage the undetected_chromedriver import and instance.
    Patched for Python 3.12+ (where distutils is removed).
    """
    _uc_module = None
    _driver = None

    @classmethod
    def _patch_distutils(cls):
        """Monkey-patch distutils before UC is imported"""
        if "distutils" not in sys.modules:
            sys.modules['distutils'] = setuptools.distutils
            sys.modules['distutils.version'] = setuptools.distutils.version

    @classmethod
    def get_uc(cls):
        """Lazy load the undetected_chromedriver module with distutils patching"""
        if cls._uc_module is None:
            cls._patch_distutils()  # Apply patch BEFORE importing UC
            try:
                import undetected_chromedriver as uc
                cls._uc_module = uc
            except ImportError as e:
                raise RuntimeError(
                    "undetected_chromedriver required. Install with: "
                    "pip install undetected-chromedriver"
                ) from e
        return cls._uc_module

    @classmethod
    def create_driver(cls, options):
        """Create a new driver instance with patched UC"""
        uc = cls.get_uc()  # Ensures patch is applied
        return uc.Chrome(options=options)