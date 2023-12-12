# TagPDF PDF标签工具

[![python](https://img.shields.io/badge/Python-≥3.10-darkcyan?logo=python&style=flat&labelColor=013243)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-≥6.6-darkcyan?logo=qt&style=flat&labelColor=013243)](https://doc.qt.io/qtforpython/)
[![sqlalchemy](https://img.shields.io/badge/sqlalchemy-≥2.0-darkcyan?logo=sqlalchemy&style=flat&labelColor=013243)](https://www.sqlalchemy.org/)

## 介绍

通过SQLITE数据库给PDF文件打标签，方便后续检索。

## 构建

双击`build.bat`即可构建。

## 使用

- 双击`TagPDF.exe`运行程序。
- 通过左侧`扫描添加`子窗口选择需要扫描的文件夹，点击`扫描选中路径`按钮开始扫描PDF。
- 扫描获得的PDF会在中间的子窗口中显示，已经跟踪路径的PDF会有底色高亮显示。
- 选择中间子窗口中的PDF，右侧上方的子窗口可以预览PDF，右侧下方的子窗口可以编辑PDF的标签。
- PDF根据公文处理的要求提供了五个属性，分别是`（公文）标题`、`（公文）文号`、`发布（单位）`、`（发文）年份`、`标签`。
- 五个属性都随着编辑框的输入而实时更新。
- 其中`标题`为必填项目，如果`标题`为空，其他属性都无法写入，如果`标题`被删除，其他属性也会被删除，并取消对该PDF的跟踪。
- `标签`属性可以根据需求进行自定义输入，每次输入完成按回车即可形成`标签`，已经存在的`标签`会有输入提示。
- 可以通过`标签`上自带的`×`按钮删除已标记的`标签`。
- 通过左侧`过滤查询`子窗口可以对已经跟踪的PDF进行过滤查询，查询结果会在中间的子窗口中显示。
- 查询的条件为`发布（单位）`、`（发文）年份`、`标签`，可以单独使用，也可以组合使用。
- 查询全部未选中的情况下，则会列示所有已经跟踪的PDF。
- 通过`导出当前列表`按钮可以将当前列出的全部PDF打包成一个ZIP文件，方便传输。
- `导出当前列表`会弹出保存路径，选择待导出的文件夹路径即可。

## 说明

- 本程序使用了`PySide6`作为GUI框架，`sqlalchemy`作为数据库框架。
- 本程序会在运行中产生一个pdf.db3文件，该文件为数据库文件，不建议手动更改或编辑。
