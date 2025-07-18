"""Generate LaTeX preprint from markdown template."""

from ..processors.template_processor import (
    generate_supplementary_tex,
    get_template_path,
    process_template_replacements,
)
from ..utils import (
    find_manuscript_md,
    write_manuscript_output,
)


def generate_preprint(output_dir, yaml_metadata):
    """Generate the preprint using the template."""
    template_path = get_template_path()
    with open(template_path) as template_file:
        template_content = template_file.read()

    # Find and process the manuscript markdown
    manuscript_md = find_manuscript_md()

    # Process all template replacements
    template_content = process_template_replacements(
        template_content, yaml_metadata, str(manuscript_md)
    )

    # Write the generated manuscript to the output directory
    manuscript_output = write_manuscript_output(output_dir, template_content)

    # Generate supplementary information
    generate_supplementary_tex(output_dir, yaml_metadata)

    return manuscript_output
