# GitHub Pages와 동일한 환경으로 로컬에서 Jekyll 사이트를 실행합니다
# 'bundle exec jekyll serve'로 실행하세요

source "https://rubygems.org"

gem "github-pages", group: :jekyll_plugins
gem "jekyll-theme-minimal"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.12"
  gem "jekyll-seo-tag"
  gem "jekyll-github-metadata"
end

# Windows 호환성
platforms :mingw, :x64_mingw, :mswin do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
end

# 성능 향상
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
