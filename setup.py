import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
	name="trakai",
	version="0.2.0",
	author="novov",
	author_email="anon185441@gmail.com",
	description="A simple blog generator designed specially to integrate into existing sites.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://novov.neocities.org/projects/trakai.html",
	license='MIT',
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Development Status :: 3 - Alpha",
		"Topic :: Internet :: WWW/HTTP",
		"Topic :: Internet :: WWW/HTTP :: Site Management"
	],
	python_requires='>=3.6',
	install_requires=[
		"jinja2>=2.11.0",
		"markdown>=3.3.0"
	],
	entry_points={
		"console_scripts": [
			"trakai=trakai.__main__:main"
		]
	}
)