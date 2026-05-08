; HoLiLiHu ReClip - Inno Setup Script
; Bộ cài đặt chuyên nghiệp - Tiếng Việt

#define MyAppName "HoLiLiHu ReClip"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "HoLiLiHu"
#define MyAppURL "https://github.com/averygan/reclip"
#define MyAppExeName "HoLiLiHu-ReClip.exe"

[Setup]
AppId={{B8F3A1E2-5D7C-4A9B-8E6F-2C1D0A3B5E7F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=.
OutputBaseFilename=HoLiLiHu-ReClip-Setup
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=110,110
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes

[Languages]
Name: "vietnamese"; MessagesFile: "compiler:Default.isl"

[Messages]
; Cửa sổ
SetupWindowTitle=Cài đặt - {#MyAppName}
; Trang chào mừng
WelcomeLabel1=Chào mừng đến với Trình cài đặt {#MyAppName}
WelcomeLabel2=Trình cài đặt sẽ cài {#MyAppName} phiên bản {#MyAppVersion} lên máy tính của bạn.%n%nỨng dụng tải video và nhạc miễn phí từ YouTube, TikTok, Instagram, Facebook và hơn 1000 nền tảng khác.%n%nNhấn Tiếp tục để bắt đầu.
; Chọn thư mục
WizardSelectDir=Chọn thư mục cài đặt
SelectDirDesc=Bạn muốn cài {#MyAppName} vào đâu?
SelectDirLabel3=Trình cài đặt sẽ cài {#MyAppName} vào thư mục sau.
SelectDirBrowseLabel=Nhấn Tiếp tục để cài đặt. Nếu muốn chọn thư mục khác, nhấn Duyệt.
; Chọn tác vụ
WizardSelectTasks=Chọn tác vụ bổ sung
SelectTasksDesc=Chọn các tác vụ bổ sung:
SelectTasksLabel2=Chọn các tác vụ bổ sung khi cài đặt {#MyAppName}, sau đó nhấn Tiếp tục.
; Sẵn sàng cài đặt
WizardReady=Sẵn sàng cài đặt
ReadyLabel1=Trình cài đặt đã sẵn sàng cài {#MyAppName} lên máy tính của bạn.
ReadyLabel2a=Nhấn Cài đặt để bắt đầu.
; Đang cài đặt
WizardInstalling=Đang cài đặt
InstallingLabel=Đang cài đặt {#MyAppName}, vui lòng chờ...
StatusExtractFiles=Đang giải nén tệp...
StatusInstalling=Đang cài đặt...
; Hoàn tất
FinishedHeadingLabel=Hoàn tất cài đặt {#MyAppName}
FinishedLabel=Ứng dụng đã được cài đặt thành công.%n%nNhấn Hoàn tất để đóng trình cài đặt.
ClickFinish=Nhấn Hoàn tất để đóng.
; Nút bấm
ButtonNext=Tiếp tục >
ButtonBack=< Quay lại
ButtonCancel=Hủy bỏ
ButtonInstall=Cài đặt
ButtonFinish=Hoàn tất
; Hộp thoại
BrowseDialogTitle=Chọn thư mục
NewFolderName=Thư mục mới
ExitSetupTitle=Thoát cài đặt
ExitSetupMessage=Cài đặt chưa hoàn tất. Nếu thoát bây giờ, ứng dụng sẽ không được cài đặt.%n%nBạn có chắc muốn thoát không?
DiskSpaceWarning=Cài đặt cần ít nhất %1 dung lượng trống nhưng hiện chỉ còn %2.%n%nBạn có muốn tiếp tục không?
; Gỡ cài đặt
ConfirmUninstall=Bạn có chắc chắn muốn gỡ cài đặt {#MyAppName} không?
UninstallStatusLabel=Vui lòng chờ trong khi {#MyAppName} đang được gỡ cài đặt.
UninstalledAll={#MyAppName} đã được gỡ cài đặt thành công.
UninstalledMost=Gỡ cài đặt {#MyAppName} hoàn tất.%n%nMột số tệp không thể xóa. Bạn có thể xóa thủ công.
; Khác
LaunchProgram=Mở {#MyAppName}
WizardInfoBefore=Thông tin
WizardInfoAfter=Thông tin

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng trên Màn hình"; GroupDescription: "Biểu tượng bổ sung:"
Name: "startmenuicon"; Description: "Tạo biểu tượng trong Start Menu"; GroupDescription: "Biểu tượng bổ sung:"

[Files]
Source: "dist\HoLiLiHu-ReClip.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ffprobe.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
Name: "{group}\Gỡ cài đặt {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenuicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Mở {#MyAppName} ngay bây giờ"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}\downloads"
