"""Parser utils for Google Cloud Pipeline Components."""
import argparse
import os


def _make_parent_dirs_and_return_path(file_path: str):
  os.makedirs(os.path.dirname(file_path), exist_ok=True)
  return file_path


def parse_default_args(args):
  """Parse default command line arguments."""
  parser = argparse.ArgumentParser(
      prog='Vertex Pipelines service launcher', description='')
  parser.add_argument(
      '--type', dest='type', type=str, required=True, default=argparse.SUPPRESS)
  parser.add_argument(
      '--project',
      dest='project',
      type=str,
      required=True,
      default=argparse.SUPPRESS)
  parser.add_argument(
      '--location',
      dest='location',
      type=str,
      required=True,
      default=argparse.SUPPRESS)
  parser.add_argument(
      '--payload',
      dest='payload',
      type=str,
      required=True,
      default=argparse.SUPPRESS)
  parser.add_argument(
      '--gcp_resources',
      dest='gcp_resources',
      type=_make_parent_dirs_and_return_path,
      required=True,
      default=argparse.SUPPRESS)
  parsed_args, _ = parser.parse_known_args(args)

  return (parser, parsed_args)