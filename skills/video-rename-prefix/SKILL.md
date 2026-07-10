---
name: "video-rename-prefix"
description: "按文件夹名+P数+顺序号重命名视频/图片文件"
---

# 视频文件重命名规则 (Prefix-Number)

## 适用场景
对按文件夹分类的媒体文件（图片、视频）进行统一化重命名，使文件名可追溯到来源文件夹。

## 命名规则

### 规则一：文件夹名末尾有 P 数（如 `(16P60MB)` 或 `[57P482M]`）

**格式：** `{去掉括号后缀的文件夹名}{NNP}-{顺序号}.{ext}`

1. 去掉末尾的 `(NNPxxx)` 或 `[NNPxxx]` 后缀
2. 提取 P 数（如 `16P`、`57P`、`52P`）
3. 按顺序编号，最小 3 位（001, 002...）

**示例：**
| 文件夹 | 文件名 |
|--------|--------|
| `B站 咬一口兔娘ovo《黄豆粉》(16P60MB)` | `B站 咬一口兔娘ovo《黄豆粉》16P-001.jpg` |
| `咬一口兔娘ovo《纯白欲缸》[57P482M]` | `咬一口兔娘ovo《纯白欲缸》57P-001.jpg` |
| `黏黏团子兔 – NO.002 特别授课 [52P-638M]` | `黏黏团子兔 – NO.002 特别授课 52P-001.jpg` |

### 规则二：文件夹名末尾无 P 数

**格式：** `{完整文件夹名}-{顺序号}.{ext}`

1. 使用完整文件夹名作为前缀
2. 按顺序编号

**示例：**
| 文件夹 | 文件名 |
|--------|--------|
| `黏黏团子兔 - 修女` | `黏黏团子兔 - 修女-001.jpg` |
| `咬一口兔娘ovo6v` | `咬一口兔娘ovo6v-001.avi` |
| `咬一口兔娘ovoB站 新7V 舞蹈视频` | `咬一口兔娘ovoB站 新7V 舞蹈视频-001.flv` |

## PowerShell 实现

```powershell
# 核心函数：提取前缀
function Get-Prefix {
    param([string]$fn)
    # 匹配末尾的 (NNPx) 或 [NNPx] 模式
    $m = [System.Text.RegularExpressions.Regex]::Match($fn, '[\(\[].*?(\d+)P.*[\)\]\]]$')
    if ($m.Success) {
        $pNum = $m.Groups[1].Value
        $baseName = $fn.Substring(0, $m.Index)
        return "$baseName${pNum}P-"
    }
    return "$fn-"
}

# 批处理脚本（按目录结构重命名）
$base = "目标根目录"
$allDirs = [System.IO.Directory]::GetDirectories($base, "*", [System.IO.SearchOption]::AllDirectories)

foreach ($dir in $allDirs) {
    $dirName = [System.IO.Path]::GetFileName($dir)
    # 跳过分辨率子目录
    if ($dirName -in @('4K','2K','1080P','720P','480P','SD','未知分辨率')) { continue }
    
    $files = [System.IO.Directory]::GetFiles($dir) | Where-Object { 
        [System.IO.Path]::GetFileName($_) -ne 'Thumbs.db' 
    } | Sort-Object
    
    if ($files.Count -eq 0) { continue }
    
    $prefix = Get-Prefix $dirName
    $padLen = [Math]::Max(3, $files.Count.ToString().Length)
    $i = 1
    
    foreach ($fp in $files) {
        $ext = [System.IO.Path]::GetExtension($fp)
        $num = $i.ToString("D$padLen")
        $newName = "$prefix$num$ext"
        $dest = [System.IO.Path]::Combine($dir, $newName)
        
        # 冲突处理：加 _N 后缀
        try {
            $tries = 1
            while ([System.IO.File]::Exists($dest)) { 
                $dest = [System.IO.Path]::Combine($dir, "${prefix}${num}_$tries$ext")
                $tries++ 
            }
            [System.IO.File]::Move($fp, $dest)
            $i++
        } catch { }
    }
}
```

## 注意事项

1. **路径含 `[` 中括号：** 必须使用 `[System.IO.Directory]::GetFiles()` 和 `[System.IO.File]::Move()`（.NET API），不能使用 PowerShell 的 `Get-ChildItem` / `Move-Item`，否则会因通配符解析错误而失败
2. **文件名冲突：** 自动加 `_N` 后缀（如 `-001_2.jpg`）
3. **跳过 Thumbs.db：** 系统缓存文件不处理
4. **排序：** 按文件名排序后顺序编号
