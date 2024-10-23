#!/bin/bash
# A helper script to quickly create a new blog post with the correct format

# Print usage and exit
show_help() {
cat << EOF
Usage: ${0##*/} [-h] "Title of your Blog Post"

A helper script to create a new blog with the correct archetype and formatting
in the repository. Simply execute this script with the title of your blog
(making sure it is in quotes) and the file will be created with the date and
slugified title ready to write!

Flags are as follows (getopt required):

    -h  display this help and exit

NOTE: hugo is required for this script, you can install it on OS X with:

    $ brew install hugo
EOF
}

# Parse command line options with getopt
OPTIND=1

while getopts h opt; do
    case $opt in
        h)
            show_help
            exit 0
            ;;
        *)
            show_help >&2
            exit 2
            ;;
    esac
done
shift "$((OPTIND-1))"

# Check input arguments
if [[ $# -ne 1 ]]; then
    if [[ $# -gt 1 ]]; then
        echo "Ensure your title is surrounded by quotes"
    fi

    show_help >&2
    exit 2
fi

# Slugify the title
TITLE=$(echo $1 | sed -e 's/ /-/g' | tr '[:upper:]' '[:lower:]')

# Create the new blog post
hugo new posts/$(date +%F)-$TITLE.md