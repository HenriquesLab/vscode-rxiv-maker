"""Utility modules for Rxiv-Maker.

This package contains utility functions for various tasks including
email encoding/decoding and other helper functions.
"""

from .citation_utils import inject_rxiv_citation
from .email_encoder import (
    decode_email,
    encode_author_emails,
    encode_email,
    process_author_emails,
)
from .file_helpers import (
    create_output_dir,
    find_manuscript_md,
    write_manuscript_output,
)
from .pdf_utils import (
    copy_pdf_to_base,
    copy_pdf_to_manuscript_folder,
    get_custom_pdf_filename,
)
from .platform import safe_console_print, safe_print

__all__ = [
    "decode_email",
    "encode_author_emails",
    "encode_email",
    "process_author_emails",
    "safe_print",
    "safe_console_print",
    "find_manuscript_md",
    "copy_pdf_to_manuscript_folder",
    "copy_pdf_to_base",
    "get_custom_pdf_filename",
    "create_output_dir",
    "write_manuscript_output",
    "inject_rxiv_citation",
]
