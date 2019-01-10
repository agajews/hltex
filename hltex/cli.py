import click
import os
from hltex.translator import Translator


@click.command()
@click.option('--out', type=click.Path(),
              help='Output file to save compiled LaTeX into (input file basename with the `.tex` extension by default)')
@click.argument('filename', type=click.Path(exists=True))
def translate(filename, out=None):
    with open(filename, 'r') as f:
        translator = Translator(f.read())
    res = translator.translate()
    if res is not None:
        if out is None:
            out = os.path.splitext(os.path.basename(filename))[0] + '.tex'
        with open(out, 'w') as f:
            f.write(res)
        print('Wrote output to `{}`'.format(out))


if __name__ == '__main__':
    translate()
