import click
import jinja2
import re
import os

@click.command()
@click.option('-r', '--replicas', type=click.INT , default=4)
@click.option('-c', '--compose-file', type=click.STRING, default='docker-compose.yml.template')
@click.option('-n', '--nginx-file', type=click.STRING, default='nginx.conf.template')
@click.option('-d', '--container-name', type=click.STRING, \
              default=[s for s in os.path.dirname(os.path.realpath(__file__)).split('/') if s != ''][-1])
@click.option('-p', '--port', type=click.INT, required=True)
def main(replicas, compose_file, nginx_file, container_name, port):
    for temp_file in (compose_file, nginx_file):
        with open(temp_file) as f:
            template = jinja2.Template(f.read())

        fn = temp_file.replace('.template', '')
        with open(fn, 'w+') as f:
            for line in template.render(replicas=replicas, container_name=container_name, \
                                        port=port).split('\n'):
                if not re.match(r'^\s*$', line):
                    f.write(line+'\n')
            print("Regenerated {}".format(fn))

if __name__ == '__main__':
    main()