import os
import pathlib

import pytest

from ansible_builder.utils import write_file, copy_file, run_command


def test_write_file(tmp_path):
    path = tmp_path / 'foo.txt'
    text = [
        'foo  # from some collection',
        'bar',
        '# a comment',
        '',
        'zoo',
        ''  # trailing line
    ]
    assert write_file(path, text)  # does not exist, write
    assert not write_file(path, text)  # already correct, do not write


def test_copy_file(dest_file, source_file):
    # modify source file, which should trigger a re-copy
    source_file.write_text('foo\nbar\nzoo')

    assert copy_file(source_file, dest_file)
    assert not copy_file(source_file, dest_file)


def test_copy_touched_file(dest_file, source_file):
    stat = pathlib.Path(source_file).stat()
    new_atime = stat.st_atime + 1
    new_mtime = stat.st_mtime + 1
    os.utime(source_file, (new_atime, new_mtime))

    assert copy_file(source_file, dest_file)
    assert not copy_file(source_file, dest_file)


def test_copy_touched_file_ignore_mtime(dest_file, source_file):
    stat = pathlib.Path(source_file).stat()
    new_atime = stat.st_atime + 1
    new_mtime = stat.st_mtime + 1
    os.utime(source_file, (new_atime, new_mtime))

    assert not copy_file(source_file, dest_file, ignore_mtime=True)


def test_copy_file_with_destination_directory(dest_file, source_file):
    # Change source file to trigger copy_file
    source_file.write_text('foo\nbar\nzoo')

    with pytest.raises(Exception) as err:
        copy_file(source_file, '/tmp')
    assert "can not be a directory" in str(err.value.args[0])

    with pytest.raises(Exception) as err:
        copy_file('/tmp', dest_file)
    assert "can not be a directory" in str(err.value.args[0])

    assert copy_file(source_file, dest_file)


@pytest.mark.run_command
def test_failed_command(mocker):
    mocker.patch('ansible_builder.utils.subprocess.Popen.wait', return_value=1)
    with pytest.raises(SystemExit):
        run_command(['sleep', '--invalidargument'])


@pytest.mark.run_command
def test_failed_command_with_allow_error(mocker):
    mocker.patch('ansible_builder.utils.subprocess.Popen.wait', return_value=1)

    rc, out = run_command(
        ['sleep', '--invalidargument'],
        allow_error=True,
    )

    assert rc == 1
    assert not out


@pytest.mark.run_command
def test_invalid_non_docker_command(caplog, mocker):
    mocker.patch('ansible_builder.utils.subprocess.Popen.wait', return_value=1)

    command = 'thisisnotacommand'
    with pytest.raises(SystemExit):
        run_command([command], capture_output=True)

    record = caplog.records[-1]  # final log message emitted

    assert f'You do not have {command} installed' in record.msg
    assert 'container-runtime' not in record.msg


@pytest.mark.run_command
def test_invalid_docker_command(caplog, mocker):
    mocker.patch('ansible_builder.utils.subprocess.Popen', side_effect=FileNotFoundError)
    mocker.patch('ansible_builder.utils.shutil.which', return_value=False)

    with pytest.raises(SystemExit):
        run_command(['docker', 'history', 'quay.io/foo/fooooo'], capture_output=True)

    record = caplog.records[-1]  # final log message emitted

    assert 'You do not have docker installed' in record.msg
    assert 'podman: not installed, docker: not installed' in record.msg
