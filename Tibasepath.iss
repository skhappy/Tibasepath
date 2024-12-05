#define MyAppName "Tibasepath"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "Tibasepath.exe"

[Setup]
AppId={{YOUR-GUID-HERE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=Tibasepath_Setup
SetupIconFile=metrohm.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "开机自动启动"; GroupDescription: "其他选项:"; Flags: unchecked

[Files]
Source: "dist\Tibasepath\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "metrohm.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\metrohm.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\metrohm.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\metrohm.ico"; Tasks: startup

[Registry]
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Tibasepath"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{userstartup}\{#MyAppName}.lnk"
Type: files; Name: "{app}\*.*"
Type: dirifempty; Name: "{app}"

[Code]
var
  SourceDirPage: TInputDirWizardPage;
  TargetDirPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  { 创建源目录选择页面 }
  SourceDirPage := CreateInputDirPage(wpSelectDir,
    '选择源文件夹', 
    '请选择需要监控的文件夹',
    '选择包含UTF8文件的源文件夹:' + #13#10#13#10 +
    '点击"浏览"按钮选择文件夹，或者直接输入路径。',
    False, '');
  SourceDirPage.Add('');
  
  { 创建目标目录选择页面 }
  TargetDirPage := CreateInputDirPage(SourceDirPage.ID,
    '选择目标文件夹',
    '请选择文件处理后的存放位置',
    '选择目标文件夹:' + #13#10#13#10 +
    '点击"浏览"按钮选择文件夹，或者直接输入路径。',
    False, '');
  TargetDirPage.Add('');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = SourceDirPage.ID then
  begin
    if SourceDirPage.Values[0] = '' then
    begin
      MsgBox('请选择源文件夹！', mbError, MB_OK);
      Result := False;
    end;
  end
  else if CurPageID = TargetDirPage.ID then
  begin
    if TargetDirPage.Values[0] = '' then
    begin
      MsgBox('请选择目标文件夹！', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  SourceDir, TargetDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigFile := ExpandConstant('{app}\tibasepath.conf');
    SourceDir := SourceDirPage.Values[0];
    TargetDir := TargetDirPage.Values[0];
    
    { 创建配置文件 }
    SaveStringToFile(ConfigFile,
      '[Paths]' + #13#10 +
      'source = ' + SourceDir + #13#10 +
      'target = ' + TargetDir + #13#10,
      False);
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  { 如果是升级安装，跳过目录选择页面 }
  if (PageID = SourceDirPage.ID) or (PageID = TargetDirPage.ID) then
    Result := WizardIsTaskSelected('startup');
end;