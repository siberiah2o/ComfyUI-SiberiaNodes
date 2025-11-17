/**
 * ComfyUI-SiberiaNodes - Frontend handler for SiberiaMultiImageLoaderNode
 *
 * Features:
 * - Dynamic input count handling
 * - State management and visual feedback
 * - Node resizing and layout management
 *
 * Author: siberiah0h
 * Email: siberiah0h@gmail.com
 * Technical Blog: www.dataeast.cn
 * Last Updated: 2025-11-17
 */

import { app } from "/scripts/app.js";

/**
 * 注册 Siberia Multi Image Loader 扩展
 * Register Siberia Multi Image Loader Extension
 */
app.registerExtension({
    name: "Siberia.MultiImageLoader",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 仅处理 SiberiaMultiImageLoaderNode 节点
        if (nodeData.name !== "SiberiaMultiImageLoaderNode") {
            return;
        }

        console.log("🎯 [Siberia MultiImageLoader] Registering SiberiaMultiImageLoaderNode");

        // 重写节点创建函数
        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;

        nodeType.prototype.onNodeCreated = function () {
            // 调用原始创建函数
            originalOnNodeCreated?.apply(this, arguments);

            // 添加自定义属性来跟踪状态
            this._siberiaImageCount = 2;
            this._siberiaLastUpdate = Date.now();

            console.log("📝 [Siberia MultiImageLoader] Node created with default image count:", this._siberiaImageCount);
        };

        // 重写onConfigure函数以处理工作流加载
        const originalOnConfigure = nodeType.prototype.onConfigure;

        nodeType.prototype.onConfigure = function () {
            // 调用原始配置函数
            originalOnConfigure?.apply(this, arguments);

            // 处理工作流加载时更新状态
            const imageCountWidget = this.widgets?.find(w => w.name === 'image_count');
            if (imageCountWidget) {
                const newCount = parseInt(imageCountWidget.value);
                this._siberiaImageCount = newCount;
                console.log("🔄 [Siberia MultiImageLoader] Node configured with image count:", newCount);
            }
        };

        // 重写onWidgetChanged函数以处理参数变化
        const originalOnWidgetChanged = nodeType.prototype.onWidgetChanged;

        nodeType.prototype.onWidgetChanged = function (widget, value) {
            // 调用原始函数
            const result = originalOnWidgetChanged?.apply(this, arguments);

            // 如果是image_count参数变化，更新状态并自动刷新输入
            if (widget.name === 'image_count') {
                const newCount = parseInt(value);
                const oldCount = this._siberiaImageCount || 2;

                // 只在数量确实改变时更新
                if (oldCount !== newCount) {
                    this._siberiaImageCount = newCount;
                    this._siberiaLastUpdate = Date.now();

                    console.log(`📝 [Siberia MultiImageLoader] Image count changed from ${oldCount} to ${newCount}`);

                    // 显示用户提示
                    const message = newCount > 2
                        ? `现在可以使用 ${newCount} 个图片输入 / Now using ${newCount} image inputs`
                        : `图片输入数量已设置为 ${newCount} / Image count set to ${newCount}`;
                    console.log(`🎯 [Siberia MultiImageLoader] ${message}`);

                    // 自动刷新节点输入 - 这是关键部分
                    this._updateImageInputs(newCount);

                    // 标记画布需要重绘
                    setTimeout(() => {
                        app.graph.setDirtyCanvas(true, false);
                    }, 100);
                }
            }

            return result;
        };

        // 添加自动更新输入的方法
        nodeType.prototype._updateImageInputs = function (newCount) {
            try {
                console.log(`🔄 [Siberia MultiImageLoader] Auto-refreshing node inputs to ${newCount} images`);

                // 直接触发节点重建 - 这是 ComfyUI 动态输入的标准做法
                setTimeout(() => {
                    // 保存节点位置和连接
                    const nodePos = [...this.pos];
                    const nodeSize = [...this.size];
                    const connections = [];

                    // 保存所有连接
                    if (this.inputs) {
                        this.inputs.forEach(input => {
                            if (input.link) {
                                connections.push({
                                    originNode: input.link.origin_node,
                                    originSlot: input.link.origin_slot,
                                    targetSlot: input.link.target_slot
                                });
                            }
                        });
                    }

                    // 保存widget值
                    const widgetValues = {};
                    if (this.widgets) {
                        this.widgets.forEach(widget => {
                            widgetValues[widget.name] = widget.value;
                        });
                    }

                    // 删除旧节点
                    app.graph.remove(this);

                    // 创建新节点
                    setTimeout(() => {
                        const newNode = app.graph.addNode(this.type, {
                            pos: nodePos,
                            size: nodeSize
                        });

                        // 恢复widget值
                        if (newNode.widgets) {
                            newNode.widgets.forEach(widget => {
                                if (widgetValues.hasOwnProperty(widget.name)) {
                                    widget.value = widgetValues[widget.name];
                                }
                            });
                        }

                        // 设置正确的input_count值
                        const countWidget = newNode.widgets.find(w => w.name === 'input_count');
                        if (countWidget) {
                            countWidget.value = newCount;
                        }

                        // 恢复连接
                        setTimeout(() => {
                            connections.forEach(conn => {
                                try {
                                    app.graph.connect(
                                        conn.originNode,
                                        conn.originSlot,
                                        newNode.id,
                                        conn.targetSlot
                                    );
                                } catch (e) {
                                    console.warn(`⚠️ [Siberia MultiImageLoader] Could not restore connection:`, e);
                                }
                            });

                            // 强制更新UI
                            app.graph.setDirtyCanvas(true, true);
                            console.log(`✅ [Siberia MultiImageLoader] Node recreated with ${newCount} inputs and connections restored`);
                        }, 100);
                    }, 50);
                }, 50);

            } catch (error) {
                console.error("❌ [Siberia MultiImageLoader] Error in auto-refresh:", error);
            }
        };

        // 添加节点大小调整逻辑
        const originalOnResize = nodeType.prototype.onResize;

        nodeType.prototype.onResize = function (size) {
            // 确保最小高度
            const minHeight = 200;
            if (size[1] < minHeight) {
                size[1] = minHeight;
            }

            // 调用原始resize函数
            originalOnResize?.apply(this, arguments);
        };

        
        console.log("✅ [Siberia MultiImageLoader] SiberiaMultiImageLoaderNode registered successfully");
    }
});