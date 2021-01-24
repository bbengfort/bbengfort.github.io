---
aliases:
- /snippets/2018/01/06/cli-editor-app.html
categories: snippets
date: '2018-01-06T09:30:58Z'
draft: false
showtoc: false
slug: cli-editor-app
title: Git-Style File Editing in CLI
---

A recent application I was working on required the management of several configuration and list files that needed to be validated. Rather than have the user find and edit these files directly, I wanted to create an editing  workflow similar to `crontab -e` or `git commit` &mdash; the user would call the application, which would redirect to a text editor like vim, then when editing was complete, the application would take over again.

This happened to be a Go app, so the following code is in Go, but it would work with any programming language. The workflow is as follows:

1. Find an editor executable
2. Copy the original to a temporary file
3. Exec the editor on the temporary file
4. Wait for the editor to be done
5. Validate the temporary file
6. Copy the temporary file to the original location

This worked surprisingly well especially for things like YAML files which are structured enough to be validated easily, but human readable enough to edit.

First up, finding an editor executable. I used a three part strategy; first the user could specify the path to an editor in the configuration file (like git), second, the user could set the `$EDITOR` environment variable, and third, I look for common editors. Here's the code:

```go
var editors = [4]string{"vim", "emacs", "nano"}

func findEditor() (string, error) {

	config, err := LoadConfig()
	if err != nil {
		return "", err
	}

	if config.Editor != "" {
		return config.Editor, nil
	}

	if editor := os.Getenv("EDITOR"); editor != "" {
		return editor, nil
	}

	for _, name := range editors {
		path, err := exec.LookPath(name)
		if err == nil {
			return path, nil
		}
	}

	return "", errors.New("no editor found")
}
```

The crucial part of this is `exec.LookPath` which searches the `$PATH` for editor and returns the full path to exec it. Next up is copying the file:

```go
func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()

	out, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer out.Close()

	if _, err = io.Copy(out, in); err != nil {
		return err
	}

	return nil
}
```

Finally the full editor workflow:

```go
func EditFile(path string) error {
	// Find the editor to use
	editor, err := findEditor()
	if err != nil {
		return err
	}

	// Create the temporary directory and ensure we clean up when done.
	tmpDir := os.TempDir()
	defer os.RemoveAll(tmpDir)

	// Get the temporary file location
	tmpFile := filepath.Join(tmpDir, filepath.Base(path))

	// Copy the original file to the tmpFile
	if err = copyFile(path, tmpFile); err != nil {
		return err
	}

	// Create the editor command
	cmd := exec.Command(editor, tmpFile)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// Start the editor command and wait for it to finish
	if err = cmd.Start(); err != nil {
		return err
	}

	if err = cmd.Wait(); err != nil {
		return err
	}

	// Copy the tmp file back to the original file
	return copyFile(tmpFile, path)
}
```

This workflow assumes that the file being edited already exists, but of course you could modify it any number of ways. For example, you could use a template to populate the temporary file (similar to what git does for a commit message), or you could add more validation around input and output. 
