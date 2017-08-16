# NVDAStore
## A fast, easy yet secure way to install and update addons within NVDA.
Version 0.6

## Introduction
This document describes how to use the NVDAStore Addon, an effective way to download install and update addons within QVDA.
The main user features of this module are:
- Easy to use interface
- A single list presenting available add-ons from various places.
- An easy way to install an add-on: simply select the desired one, press Install, and you're done.
- Notify you when an update is available: Simply press Update on the add-on to update it to the latest version supported by your NVDA.
- Shows what's really working: Some checks are made to ensure the add-on you'll install will work on your system.

This add-on also provides features for developers:
- Capability check: You can flag your add-on to work only if certain features are present on the target system, such as TouchScreen, or a specific Windows version or build.
- No need to notify users: Simply post a new release to the store to allow users to download and update it rightaway, if their system is compatible.
- Addon storage: Your add-on is stered on our servers to maximize bandwidth.
- Some much more fun features will be available in the near future.

This document is divided into two main sections:
- User Guide: This primary section is used to describe how to use the add-on itself.
- Developer Guide: If you are a NVDA Add-on Developer, this section will get you step-by-step to a successful publishing into the NVDAStore.

## User Guide
### Installation
This add-on installs like any other NVDA add-on. You can download it from the following URL:
- [Cecitek-0.5.nvda-addon](https://github.com/YPlassiard/nvda-cecitek/)

When downloaded, double-click the "cecisek-x.y.nvda-addon" file to initiate the install process, while NVDA is running. When the install completes, NVDA needs to be restarted before using the add-on for the first time.

### Opening the NVDAStore
To open the NVDAStore, you can press the _NVDA+Shift+C_ shortcut. Please note that it's always possible to change this shortcut in the NVDA Gesture preference dialog.
Note that, depending on your internet connection, the store may take a few secons to pop-up, please be patient.

### The NVDAStore dialog
This dialog contains four main areas which are described below:
- The modules' list: contains available NVDA add-ons with their respective state:
- - up-to-date: The add-on is installed and up-to-date.
- - Update available: an update is available for the selected add-on.
- - Not installed: This add-on is not installed.
- - Disabled: This add-on has been disabled by the user.
- Categories' list: Contains the currently available categories. When changing category, the module's list is refreshed to show related results.
- Description: this multi-line text field contains some information regarding the selected add-on such as its description, and the last version's changelog.
- Some buttons: When an add-on is selected, some buttons are present to execute actions against this add-on such as:
- - enable/disable: disable the add-on, keeping it installed but not loading it on NVDA startup.
- - about: Shows some information regarding the add-on such as summary, author, version, and homepage.
- - install/update: allows you to install or update (if already installed and new version available) the selected add-on.
- - remove: uninstalls the selected add-on.
- - close: closes the NVDAStore.

When clicking on the "Close" button, NVDA automatically restarts if needed (if you made some modifications such as installing, enabling, disabling or removing an add-on). 

### Configuring the NVDAStore.
If you're using an Internet connection that requires a proxy, you can set it up manually for now, following these steps:
- Press _Windows+R_ to open the run dialog.
- If you're using an installed copy of NVDA:
- - Enter "%AppData%\Roaming\NVDA\Addons" in the text field.
- If you're using a portable copy of NVDA:
- - Go to the location where you started the portable copy, and then enter the "userConfig\Addon" directory.

Then, create a simple text file with your favorite editor (may be Notepad for example), and paste the following content:
```
{
  "proxies": {
    "http"": "your_http_proxy:proxy_port",
    "ftp": "your_ftp_proxy:proxy_port",
    "https": "your_https_proxy:proxy_port"
  }
}
```

Save the file as "cecitek.json" and restart NVDA for the changes to be effective. Please note that the ".json" extension is very important, and be careful of certain editors that automatically adds a ".txt" extension at the en of the filename. If you are in this situation, simply rename the file using the Windows Explorer.
### Issues and bug-reports

For issues and bug-reports, feel free to either:
- Open an [Issue on GitHub](https://github.com/YPlassiard/nvda-cecitek/issue/new)
- Or if you're not familiar with GitHub, [Send a mail](mailto:podcastcecitek@gmail.com) to the team.

## Developer's Guide
This section describes what you need to do to publish xour add-on into the NVDAStore. We strongly encourage you to use GitHub to host your add-on's source code because our update checker script works perfectly well with the GitHub Releases feature. However, it's completely possible to benefit from all NVDAStore features without a GitHub repository.
### Architecture description
The store can be divided in two parts:
- The server-side APIs
- And the NVDAStore Clients (such as this NVDA Add-on, as well as the front-end component of the Cecitek website).

#### Server-side APIs
Like many other services, and therefore many other software stores, the server is responsible for answering user requests such as:
- Get a list of all add-ons.
- Get a list of all categories.
- Retrieve all versions for a specified add-on.
- Download the binary file associated to a specific version.

#### NVDAStore Client
The client is responsible for sending requests to the server depending on the user's actions and its configuration, to list and download add-ons. It will also, for the NVDA Add-on client, install the freshly downloaded add-on automatically.

### Typical workflow
The following sequence illustrates a typical user session:
- The user press _NVDA+Shift+C_
- The NVDAStore client connects to the server and asks for an updated list of all available add-ons.
- At the same time, it also asks for a list of all known add-on's categories.
- When receiving results, it runs some capability checks upon each add-on version to determine whether an add-on is installable or updatable.
- It then builds the user-interface with relevant information.
- When the user clicks on the "Update" or "Install" button, the client asks the server for the add-on binary matching the desired version.
- When all data has been received, the downloaded add-on issaved to a temporarx file and the installation process starts.
