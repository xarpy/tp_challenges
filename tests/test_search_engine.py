import os
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

from scripts.search_engine import BuildManager, GoogleDriveAPI, MetaEngine


@pytest.mark.parametrize(
    "os_conditional, mock_credentials, mock_flow, cred_valid, cred_expired, refresh_token",
    [
        (True, MagicMock(), MagicMock(), True, False, False),
        (False, MagicMock(), MagicMock(), False, False, False),
        (True, MagicMock(), MagicMock(), True, True, True),
    ],
)
@patch("builtins.open", new_callable=mock_open, read_data="token.json")
@patch("scripts.search_engine.get_filepath")
@patch("scripts.search_engine.Credentials")
@patch("scripts.search_engine.InstalledAppFlow")
@patch("scripts.search_engine.os")
@patch("scripts.search_engine.build")
def test_get_session(
    mock_build,
    mock_os,
    mock_class_flow,
    mock_class_cred,
    mock_get_filepath,
    mock_file,
    os_conditional,
    mock_credentials,
    mock_flow,
    cred_valid,
    cred_expired,
    refresh_token,
) -> None:
    """Test GoogleDriveAPI.get_session function"""
    mock_credentials.valid = cred_valid
    mock_credentials.expired = cred_expired
    mock_credentials.refresh_token = refresh_token

    mock_get_filepath.return_value = os.environ["CREDENTIAL_FILENAME"]
    mock_os.path.exists.return_value = os_conditional
    if os_conditional:
        mock_class_cred.from_authorized_user_file.return_value = (
            mock_credentials
        )
    if not cred_valid:
        mock_flow.run_local_server.return_value = mock_credentials
        mock_class_flow.from_client_secrets_file.return_value = mock_flow

    testclass = GoogleDriveAPI()
    testclass.get_session()
    mock_build.assert_called_with("drive", "v3", credentials=mock_credentials)


@pytest.mark.parametrize(
    "items, expected",
    [
        (
            [
                {
                    "id": 1,
                    "name": "Test",
                    "mimeType": "document",
                    "modifiedTime": "1990-01-01",
                }
            ],
            {
                "message": "Files:",
                "data": "  ID  Name    Parents    Size    Type      Modified Time\n----  ------  ---------  ------  --------  ---------------\n   1  Test    N/A        N/A     document  1990-01-01",
            },
        ),
        (
            [],
            {"message": "No files found."},
        ),
    ],
)
def test_list_files(items, expected) -> None:
    """Test GoogleDriveAPI.list_files function"""
    testclass = GoogleDriveAPI()
    result = testclass.list_files(items)
    assert result == expected


@pytest.mark.parametrize(
    "byte, factor, suffix, expected",
    [
        (8, 1024, "B", "8.00B"),
        (16, 1024, "B", "16.00B"),
    ],
)
def test_get_size_format(byte, factor, suffix, expected) -> None:
    """Test GoogleDriveAPI.get_size_format function"""
    testclass = GoogleDriveAPI()
    result = testclass.get_size_format(byte, factor, suffix)
    assert result == expected


@pytest.mark.parametrize(
    "mock_session, items, list_files",
    [
        (
            MagicMock(),
            {
                "files": [
                    {
                        "id": 1,
                        "name": "Test",
                        "mimeType": "document",
                        "modifiedTime": "1990-01-01",
                    }
                ]
            },
            {
                "message": "Files:",
                "data": "  ID  Name    Parents    Size    Type      Modified Time\n----  ------  ---------  ------  --------  ---------------\n   1  Test    N/A        N/A     document  1990-01-01",
            },
        ),
        (
            MagicMock(),
            {},
            {"message": "No files found."},
        ),
    ],
)
@patch("scripts.search_engine.GoogleDriveAPI.list_files")
@patch("scripts.search_engine.GoogleDriveAPI.get_session")
@patch("scripts.search_engine.logger")
def test_show_itens(
    mocked_logger,
    mocked_get_session,
    mocked_list_files,
    mock_session,
    items,
    list_files,
) -> None:
    """Test GoogleDriveAPI.show_itens function"""
    mocked_get_session.return_value = mock_session
    mock_session.files().list().execute().return_value = items
    mocked_list_files.return_value = list_files
    testclass = GoogleDriveAPI()
    testclass.show_itens()
    if list_files.get("data"):
        calls = [call(list_files.get("message")), call(list_files.get("data"))]
        mocked_logger.info.assert_has_calls(calls, any_order=True)
    else:
        mocked_logger.info.assert_called_with(list_files.get("message"))


@pytest.mark.parametrize(
    "list_name",
    [
        ([{"name": "thinking_out_the_box"}]),
    ],
)
@patch("scripts.search_engine.load")
def test_extract_texts(mock_load, list_name):
    """Test MetaEngine._extract_texts function"""
    testclass = MetaEngine()
    testclass._extract_texts(list_name)
    mock_load().pipe.assert_called_once()


@pytest.mark.parametrize(
    "phrase, expected",
    [
        ("thinking_out_the_box", "thinking out the box"),
    ],
)
def test_handle_phrase(phrase, expected):
    """Test MetaEngine.handle_phrase function"""
    testclass = MetaEngine()
    result = testclass.handle_phrase(phrase)
    assert result == expected


@pytest.mark.parametrize(
    "phrase, keyword, has_found",
    [
        ("thinking_out_the_box", "box", True),
        ("thinking_out_the_box", "rice", False),
    ],
)
@patch("scripts.search_engine.Matcher")
@patch("scripts.search_engine.logger")
def test_data_processing(
    mocked_logger, mocked_matcher, phrase, keyword, has_found
):
    """Test MetaEngine._data_processing function"""
    doc = MagicMock(name="DOC")
    ents = MagicMock(name="ENTS", label_=phrase, text=phrase)
    doc.ents = [ents]
    documents = [doc]
    mocked_matcher().return_value = has_found
    testclass = MetaEngine()
    testclass._data_processing(documents, keyword)
    if has_found:
        mocked_logger.info.assert_called_once()


@pytest.mark.parametrize(
    "name_list, keywords",
    [
        ([{"name": "thinking_out_the_box"}, {"name": "Duna"}], "box"),
    ],
)
@patch("scripts.search_engine.MetaEngine._data_processing")
def test_output(mocked_data_processing, name_list, keywords):
    """Test MetaEngine.output function"""
    testclass = MetaEngine()
    testclass.output(name_list, keywords)
    mocked_data_processing.assert_called_once()


@pytest.mark.parametrize(
    "mocked_session, list_files, arguments, show_list",
    [
        (
            MagicMock(),
            {
                "files": [
                    {
                        "id": 1,
                        "name": "thinking_out_the_box",
                        "mimeType": "document",
                        "modifiedTime": "1990-01-01",
                    }
                ]
            },
            ([0]),
            True,
        ),
        (
            MagicMock(),
            {
                "files": [
                    {
                        "id": 1,
                        "name": "thinking_out_the_box",
                        "mimeType": "document",
                        "modifiedTime": "1990-01-01",
                    }
                ]
            },
            ([0, "box"]),
            False,
        ),
    ],
)
@patch("scripts.search_engine.MetaEngine.output")
@patch("scripts.search_engine.GoogleDriveAPI.get_session")
@patch("scripts.search_engine.GoogleDriveAPI.show_itens")
def test_main(
    mocked_show_itens,
    mocked_get_session,
    mocked_output,
    mocked_session,
    list_files,
    arguments,
    show_list,
):
    """Test BuildManager.main function"""
    mocked_get_session.return_value = mocked_session
    mocked_session.files().list().execute().return_value = list_files
    testclass = BuildManager()
    testclass.main(arguments)
    if show_list:
        mocked_show_itens.assert_called_once()
    else:
        mocked_output.assert_called_once()
