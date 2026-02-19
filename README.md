# Node Editor

![Logo](images/logo.png)

A node editor which creates beautiful diagrams very fast. With vim-like keyboard shortcuts


# Install
```sh
uv sync
```

# Run

```sh
uv run node-editor
```

# Controls

__TODO__: maybe add flowchart for program flow

**\<Escape\>**: Brings you back to normal mode and deselects everything

## Normal mode

**h**: move curser or selection to left

**j**: move curser or selection to down

**k**: move curser or selection to up

**l**: move curser or selection to right

**v**: change to Visual mode

**c**: change to Connect mode

**\<colon\>**: enter command mode

**x**: delte object under curser or selection

**u** / **r**: undo / redo (works for delete and add)

## Visual mode

Press any letter apearing on the screen selects that object. While pressing shift adds that object to selection

**v**: Enter normal mode with selection

## Connect mode

Press any letter apearing on the screen once to start an edge and the next letter sets the target.

## Commands

**:q**: quit

**:o path/to/file**: open a file

**:w**: save current file

**:c** or **:clear**: clear canvas

**:grid**: toggle gird

**:debug**: toggle debug

...