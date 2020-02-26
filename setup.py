from setuptools import setup

setup(
    name="Orange3-Glueviz",
    version="0.1.0",
    author="Jean Ye, China",
    author_email="1793893070@qq.com",
    description=("Orange add-on for calling Glueviz within Orange."),
    url="https://github.com/icejean/orange3-glueviz",
    platforms = "any",
    license = "GPL-3.0",
    keywords="Glueviz,data visualization,orange3 add-on",
    packages=["glueviz"],
    package_data={"glueviz": ["icons/*.*"]},
    
    # install_requires=["orange3>=3.24.1",
    #                   "anyqt>=0.0.10",
    #                   "sortedcollections>=1.1.2",
    #                   "sip>=4.19.8",
    #                   "glueviz>=0.15.2"],
    
    classifiers=["Programming Language :: Python",
    				"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
					"Operating System :: OS Independent",
					"Topic :: Scientific/Engineering :: Visualization",
					"Topic :: Software Development :: Libraries :: Python Modules",
					"Intended Audience :: Education",
					"Intended Audience :: Science/Research",
					"Intended Audience :: Developers"],
# Declare glueviz package to contain widgets for the "Glueviz" category
    entry_points={"orange.widgets": "Glueviz = glueviz"},
    zip_safe=False
)