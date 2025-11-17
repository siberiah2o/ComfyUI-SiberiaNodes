/**
 * ComfyUI-SiberiaNodes - Dynamic Input System for SiberiaMultiImageLoaderNode
 *
 * Features:
 * - Dynamic image input generation based on input_count
 * - Support for IMAGE input types only
 * - Real-time input management and refresh functionality
 *
 * Author: siberiah0h
 * Email: siberiah0h@gmail.com
 * Technical Blog: www.dataeast.cn
 * Last Updated: 2025-11-17
 */

import { app } from "/scripts/app.js";

/**
 * Siberia Dynamic Input Manager
 */
class SiberiaDynamicInputManager {
    /**
     * 更新输入数量
     */
    static updateInputCount(node, targetCount) {
        if (!node.inputs) return;

        const inputType = "image"; // Only handle image inputs now
        const currentInputs = this.getCurrentInputs(node, inputType);
        const currentCount = currentInputs.length;

        // Remove excess inputs
        if (targetCount < currentCount) {
            for (let i = currentCount; i > targetCount; i--) {
                const inputName = `${inputType}_${i}`;
                const inputIndex = this.findInputIndex(node, inputName);
                if (inputIndex !== -1) {
                    node.removeInput(inputIndex);
                }
            }
        }

        // Add new inputs
        if (targetCount > currentCount) {
            for (let i = currentCount + 1; i <= targetCount; i++) {
                const inputName = `${inputType}_${i}`;
                const inputTypeValue = "IMAGE";
                node.addInput(inputName, inputTypeValue);
            }
        }

        // Update node layout
        this.updateNodeLayout(node);
        app.graph.setDirtyCanvas(true, false);
    }

    /**
     * 获取当前指定类型的输入
     */
    static getCurrentInputs(node, inputType) {
        if (!node.inputs) return [];

        const prefix = inputType + "_";
        return node.inputs.filter(input =>
            input.name && input.name.startsWith(prefix)
        );
    }

    /**
     * 查找输入索引
     */
    static findInputIndex(node, inputName) {
        if (!node.inputs) return -1;
        return node.inputs.findIndex(input => input.name === inputName);
    }

    /**
     * 更新节点布局
     */
    static updateNodeLayout(node) {
        requestAnimationFrame(() => {
            const inputCount = this.getCurrentInputs(node, "image").length;
            const targetHeight = Math.max(200, 120 + (inputCount * 25));
            const targetWidth = Math.max(250, node.size[0]);

            if (targetHeight !== node.size[1] || targetWidth !== node.size[0]) {
                node.onResize?.([targetWidth, targetHeight]);
                app.graph.setDirtyCanvas(true, false);
            }
        });
    }

    /**
     * 查找控件
     */
    static findWidget(node, widgetName) {
        if (!node.widgets) return null;
        return node.widgets.find(widget => widget.name === widgetName);
    }
}

/**
 * 注册扩展
 */
app.registerExtension({
    name: "Siberia.DynamicInputs",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "SiberiaMultiImageLoaderNode") {
            return;
        }

        console.log("🎯 [SiberiaDynamicInput] Registering SiberiaMultiImageLoaderNode");

        // 重写节点创建函数
        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;

        nodeType.prototype.onNodeCreated = function () {
            originalOnNodeCreated?.apply(this, arguments);

            // 添加刷新控件
            this.addWidget("button", "刷新 / Refresh", null, () => {
                const inputCountWidget = SiberiaDynamicInputManager.findWidget(this, "input_count");

                if (inputCountWidget) {
                    const targetCount = parseInt(inputCountWidget.value);
                    SiberiaDynamicInputManager.updateInputCount(this, targetCount);

                    console.log(`🔄 [SiberiaDynamicInput] Refreshed to ${targetCount} image inputs`);
                }
            });

            // 初始化默认输入
            setTimeout(() => {
                const inputCountWidget = SiberiaDynamicInputManager.findWidget(this, "input_count");

                if (inputCountWidget) {
                    const initialCount = parseInt(inputCountWidget.value);
                    SiberiaDynamicInputManager.updateInputCount(this, initialCount);
                }
            }, 100);
        };

        // 重写onConfigure函数以处理工作流加载
        const originalOnConfigure = nodeType.prototype.onConfigure;

        nodeType.prototype.onConfigure = function () {
            originalOnConfigure?.apply(this, arguments);

            setTimeout(() => {
                const inputCountWidget = SiberiaDynamicInputManager.findWidget(this, "input_count");

                if (inputCountWidget) {
                    const savedCount = parseInt(inputCountWidget.value);
                    SiberiaDynamicInputManager.updateInputCount(this, savedCount);
                }
            }, 100);
        };

        // 重写onWidgetChanged函数以处理参数变化
        const originalOnWidgetChanged = nodeType.prototype.onWidgetChanged;

        nodeType.prototype.onWidgetChanged = function (widget, value) {
            const result = originalOnWidgetChanged?.apply(this, arguments);

            if (widget.name === "input_count") {
                const targetCount = parseInt(value);
                SiberiaDynamicInputManager.updateInputCount(this, targetCount);
            }

            return result;
        };

        // 添加节点大小调整逻辑
        const originalOnResize = nodeType.prototype.onResize;

        nodeType.prototype.onResize = function (size) {
            const minHeight = 200;
            const minWidth = 250;

            if (size[1] < minHeight) {
                size[1] = minHeight;
            }
            if (size[0] < minWidth) {
                size[0] = minWidth;
            }

            originalOnResize?.apply(this, arguments);
        };
    }
});