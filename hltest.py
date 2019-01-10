import hlbox

hlbox.configure(
    profiles=[
        hlbox.Profile('python', 'jupyter/scipy-notebook')
    ]
)
files = [{'name': 'main.py', 'content': b'print(43)'}]
limits = {'cputime': 1, 'memory': 64}
result = hlbox.run('python', 'python3 main.py', files=files, limits=limits, download_target='/tmp/hlbox')
print(result)

