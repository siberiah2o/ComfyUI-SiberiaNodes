/**
 * Siberia Display Node - Frontend Widget Handler
 * Siberia 显示节点 - 前端组件处理器
 *
 * 功能 / Features:
 * - 动态创建文本显示组件 / Dynamically create text display widgets
 * - 自动调整节点大小 / Auto-resize node
 * - 支持工作流保存和恢复 / Support workflow save and restore
 */

import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

/**
 * 显示节点管理器
 * Display Node Manager
 */
class SiberiaDisplayManager {
  /**
   * 填充节点的文本显示组件
   * Populate node with text display widgets
   *
   * @param {Object} node - 节点对象 / Node object
   * @param {Array} textData - 要显示的文本数据数组 / Text data array to display
   */
  static populateTextWidgets(node, textData) {
    // 移除现有的文本组件
    this.removeExistingTextWidgets(node);

    // 为每个文本项创建新的显示组件
    this.createTextWidgets(node, textData);

    // 调整节点大小以适应内容
    this.resizeNodeToFitContent(node);
  }

  /**
   * 移除现有的文本显示组件
   * Remove existing text display widgets
   *
   * @param {Object} node - 节点对象 / Node object
   */
  static removeExistingTextWidgets(node) {
    if (!node.widgets) {
      return;
    }

    // 找到第一个文本组件的位置
    const textWidgetIndex = node.widgets.findIndex((w) => w.name === "text");

    if (textWidgetIndex !== -1) {
      // 移除所有文本组件
      for (let i = textWidgetIndex; i < node.widgets.length; i++) {
        node.widgets[i].onRemove?.();
      }
      node.widgets.length = textWidgetIndex;
    }
  }

  /**
   * 创建文本显示组件
   * Create text display widgets
   *
   * @param {Object} node - 节点对象 / Node object
   * @param {Array} textData - 文本数据数组 / Text data array
   */
  static createTextWidgets(node, textData) {
    for (const text of textData) {
      const widget = ComfyWidgets["STRING"](
        node,
        "text",
        ["STRING", { multiline: true }],
        app
      ).widget;

      // 配置组件为只读模式
      this.configureReadOnlyWidget(widget, text);
    }
  }

  /**
   * 配置组件为只读模式
   * Configure widget as read-only
   *
   * @param {Object} widget - 组件对象 / Widget object
   * @param {string} value - 显示值 / Display value
   */
  static configureReadOnlyWidget(widget, value) {
    widget.inputEl.readOnly = true;
    widget.inputEl.style.opacity = 0.6;
    widget.inputEl.style.cursor = "default";
    widget.value = value;
  }

  /**
   * 调整节点大小以适应内容
   * Resize node to fit content
   *
   * @param {Object} node - 节点对象 / Node object
   */
  static resizeNodeToFitContent(node) {
    requestAnimationFrame(() => {
      const computedSize = node.computeSize();
      const newSize = [
        Math.max(computedSize[0], node.size[0]),
        Math.max(computedSize[1], node.size[1]),
      ];

      node.onResize?.(newSize);
      app.graph.setDirtyCanvas(true, false);
    });
  }
}

/**
 * 注册 Siberia Display 扩展
 * Register Siberia Display Extension
 */
app.registerExtension({
  name: "Siberia.Display",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    // 仅处理 SiberiaUniversalDisplayNode 节点
    if (nodeData.name !== "SiberiaUniversalDisplayNode") {
      return;
    }

    console.log("🎯 [Siberia Display] Registering SiberiaUniversalDisplayNode");

    // 重写节点执行后的回调
    this.setupOnExecutedCallback(nodeType);

    // 重写节点配置回调（用于工作流加载）
    this.setupOnConfigureCallback(nodeType);

    console.log(
      "✅ [Siberia Display] SiberiaUniversalDisplayNode registered successfully"
    );
  },

  /**
   * 设置节点执行后的回调
   * Setup callback after node execution
   *
   * @param {Function} nodeType - 节点类型 / Node type
   */
  setupOnExecutedCallback(nodeType) {
    const originalOnExecuted = nodeType.prototype.onExecuted;

    nodeType.prototype.onExecuted = function (message) {
      // 调用原始回调
      originalOnExecuted?.apply(this, arguments);

      // 处理显示数据
      if (message?.text) {
        console.log("📝 [Siberia Display] Received data:", message.text);
        SiberiaDisplayManager.populateTextWidgets(this, message.text);
      }
    };
  },

  /**
   * 设置节点配置回调（工作流加载时）
   * Setup callback for node configuration (workflow loading)
   *
   * @param {Function} nodeType - 节点类型 / Node type
   */
  setupOnConfigureCallback(nodeType) {
    const originalOnConfigure = nodeType.prototype.onConfigure;

    nodeType.prototype.onConfigure = function () {
      // 调用原始回调
      originalOnConfigure?.apply(this, arguments);

      // 恢复保存的组件值
      if (this.widgets_values?.length) {
        console.log(
          "🔄 [Siberia Display] Restoring widgets:",
          this.widgets_values
        );
        SiberiaDisplayManager.populateTextWidgets(this, this.widgets_values);
      }
    };
  },
});
