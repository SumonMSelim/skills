# Icon pack

Download the official "AWS Architecture Icons" asset package (SVG) from
https://aws.amazon.com/architecture/icons/ and unzip it. Point `AWS_ICONS` at the folder
that contains `Architecture-Service-Icons_*`, `Resource-Icons_*`, `Architecture-Group-Icons_*`.

    export AWS_ICONS="$HOME/Downloads/Asset-Package"

Naming inside the pack:
- Services: `Arch_<Service>_64.svg` (also 16/32/48). Use 64.
- Resources: `Res_<Service>_<Resource>_48.svg`; generic ones have `_Light`/`_Dark` variants.
  Use `_Light` on the white panel.
- Groups: `<Group>_32.svg` in Architecture-Group-Icons.

Look a name up without guessing:

    python scripts/awsdiag.py icons "kinesis"
    python scripts/awsdiag.py icons "vpc endpoint" --all

Add it to a diagram without editing the library:

    Diagram(..., extra_icons={"bedrock": "Arch_Amazon-Bedrock_64.svg"})

Icons that are not AWS (Cloudflare, GitHub, Datadog) are not in the pack. Draw a simple
shape or use a generic resource icon (`saas`-style: `app`, `server`, `internet`) and label it.
Do not embed third-party logos pulled from the web.

The AWS icons are licensed for use in architecture diagrams; keep the pack out of the skill
folder and out of git so it does not get redistributed.
