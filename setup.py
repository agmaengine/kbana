import setuptools
setuptools.setup(
    include_package_data=True,
    packages=['kbana'],
    pakage_dir={"": "src"},
    # using MANIFEST.in instead
    # package_data={
    #     "kbana": ["analysis/maps/*.json",
    #               "analysis/misc/*.png",
    #               "analysis/keyboard_styles/MainType/blank/*",
    #               "capture/misc/*.json"]
    # }
)
