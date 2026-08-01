# Minecraft World Trimmer

Is your Minecraft world getting too fat? Delete unused chunks using this software.

It finds regions in your world that has low usage and deletes them, giving you more space.

## Usage (CLI)

Right now, there is *only* a command line edition. I intend to make a TUI or GUI version later, but not now. The command line edition is accessible through `main.py`. I estimate that a threshold of 10 minutes per region (If the region has been lived in for more than 10 minutes) is a good conservative default threshold value. To use it, simply run `python3 main.py [directory]`. `directory` must point to a specific subfolder of a world folder.

Before 26.1, the directory that you must specify to this program is either the root world folder or root world/DIM-1 or DIM1. This has changed in 2026. Now, you must specify the root world folder/dimensions/the name of the world. Whatever you choose, it has to have the "region" folder in it.

This program is multiprocessed. By default it uses all CPU cores available to it. To specify a custom amount, do `-c <num>`

This program displays a live-updating progress counter by default. To shut it up, supply `-q`. To make it update faster or slower, supply `-u <float>` where the float is a number of seconds between each progress update.

If you really want to spam up your console, supply `-v`. 

## Usage (GUI)

This will come in the future

## Installing

Due to how this program operates, it is not possible to produce an EXE for it. Therefore, you must have python on your computer to run this program.