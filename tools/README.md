# 工具目錄 (Tools)

這個資料夾包含各種開發和調整工具。

## 工具列表

### pose_tool.py
姿勢編輯器 - 用於創建和編輯角色姿勢
- 互動式調整身體各部位的角度和位置
- 保存姿勢到 JSON 格式
- 自動更新 animation.py 中的姿勢定義

使用方法:
```bash
python tools/pose_tool.py
```

### adjust_tool.py
身體比例調整工具 - 用於調整角色身體部位的長度比例
- 實時預覽調整效果
- 保存配置到 body_parts_config.json

使用方法:
```bash
python tools/adjust_tool.py
```

### auto_watch.py
自動監測工具 - 監測文件變化並自動執行動作
- 用於開發時自動重新載入配置

### style_config.py
像素風格配置工具 - 調整像素化效果參數
- 設定像素大小
- 設定調色板顏色數量

### compare_images.py
圖像比較工具 - 比較不同像素化方法的效果差異
- 用於測試和評估視覺效果

## 注意事項

- 這些工具是開發和調整用途,不影響 main.py 的運行
- pose_tool.py 需要 update_animation.py(位於主目錄)來更新姿勢定義
