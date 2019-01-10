import hlbox

hlbox.configure(
    profiles=[
        hlbox.Profile('python', 'czentye/matplotlib-minimal')
    ]
)
files = [{'name': 'folder/main.py', 'content': b'import matplotlib;print(43)'}]
limits = {'cputime': 1, 'memory': 64}
result = hlbox.run('python', 'python3 folder/main.py', files=files, limits=limits, download_target='/tmp/hlbox')
print(result)

