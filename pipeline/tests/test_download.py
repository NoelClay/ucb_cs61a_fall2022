from pathlib import Path
from unittest.mock import patch, MagicMock


def test_build_output_path():
    from pipeline.modules.download import build_output_path
    path = build_output_path("lecture_01", "/data/00_raw")
    assert path == Path("/data/00_raw/lecture_01.mp4")


def test_download_skips_existing_file(tmp_path):
    from pipeline.modules.download import download_video
    output = tmp_path / "lecture_01.mp4"
    output.write_bytes(b"fake video data")
    result = download_video("https://fake-url", output)
    assert result == output  # 다운로드 없이 기존 파일 반환


def test_download_calls_yt_dlp(tmp_path):
    from pipeline.modules.download import download_video
    output = tmp_path / "lecture_01.mp4"

    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl = MagicMock()
        mock_ydl_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_cls.return_value.__exit__ = MagicMock(return_value=False)

        # yt_dlp를 pipeline.modules.download 네임스페이스에서 패치
        with patch.dict("sys.modules", {"yt_dlp": MagicMock(YoutubeDL=mock_ydl_cls)}):
            download_video("https://bilibili.com/video/test", output)

    mock_ydl_cls.assert_called_once()


def test_download_all_skips_comments(tmp_path):
    import csv
    from pipeline.modules.download import download_all

    csv_path = tmp_path / "video_list.csv"
    csv_path.write_text(
        "video_id,title,type,bilibili_url\n"
        "#comment_row,ignored,ignored,ignored\n"
        "lecture_01,Lecture 1,lecture,https://fake-url\n"
    )

    called_urls = []

    def fake_download(url, output):
        called_urls.append(url)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"data")
        return output

    with patch("pipeline.modules.download.download_video", side_effect=fake_download):
        download_all(str(csv_path), str(tmp_path / "00_raw"))

    assert called_urls == ["https://fake-url"]
