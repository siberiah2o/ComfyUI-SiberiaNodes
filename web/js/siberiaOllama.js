// Siberia Ollama Nodes - Dynamic model loading functionality
// Siberia Ollama 节点 - 动态模型加载功能

import { app } from "/scripts/app.js";

// Global manager instance
const siberiaManager = {
  modelsCache: new Map(),
  statusMessageTimeout: null,

  showStatus(message, type = "info") {
    // Clear existing timeout
    if (this.statusMessageTimeout) {
      clearTimeout(this.statusMessageTimeout);
    }

    // Create or update status element
    let statusEl = document.getElementById("siberia-status");
    if (!statusEl) {
      statusEl = document.createElement("div");
      statusEl.id = "siberia-status";
      statusEl.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                padding: 8px 12px;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                z-index: 10000;
                max-width: 300px;
                word-wrap: break-word;
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
            `;
      document.body.appendChild(statusEl);
    }

    // Set style based on type
    const colors = {
      success: "#28a745",
      error: "#dc3545",
      info: "#17a2b8",
      warning: "#ffc107",
    };

    statusEl.style.backgroundColor = colors[type] || colors.info;
    statusEl.textContent = message;

    // Show status
    setTimeout(() => {
      statusEl.style.opacity = "1";
    }, 10);

    // Auto hide after 3 seconds
    this.statusMessageTimeout = setTimeout(() => {
      statusEl.style.opacity = "0";
    }, 3000);
  },

  async fetchModels(serverName) {
    try {
      this.showStatus(`正在连接服务器 ${serverName}...`, "info");

      const response = await fetch("/siberia_ollama/get_models_by_name", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          server_name: serverName,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success && data.models && data.models.length > 0) {
        this.modelsCache.set(serverName, data.models);
        this.showStatus(
          `成功连接到 ${serverName}，找到 ${data.models.length} 个模型`,
          "success"
        );

        // Update all SiberiaOllamaConnector nodes with these models
        this.updateAllNodeModelOptions(serverName, data.models, true);

        return data.models;
      } else {
        this.showStatus(`连接失败: ${data.error || "未知错误"}`, "error");
        // Update all nodes to show only refresh option on failure
        this.updateAllNodeModelOptions(serverName, [], false);
        return [];
      }
    } catch (error) {
      console.error("❌ Error fetching Ollama models:", error);
      this.showStatus(`获取模型失败: ${error.message}`, "error");
      // Update all nodes to show only refresh option on error
      this.updateAllNodeModelOptions(serverName, [], false);
      return [];
    }
  },

  updateAllNodeModelOptions(serverName, models, autoSelectFirst = false) {
    // Update model options for all SiberiaOllamaConnector nodes
    if (app && app.graph && app.graph.nodes) {
      const nodes = app.graph.nodes;
      nodes.forEach((node) => {
        if (node.type === "SiberiaOllamaConnector") {
          const modelWidget = node.widgets?.find((w) => w.name === "model");
          const serverWidget = node.widgets?.find(
            (w) => w.name === "server_name"
          );

          if (
            modelWidget &&
            serverWidget &&
            serverWidget.value === serverName
          ) {
            // For STRING widgets, we need to find and update custom dropdown
            const options = ["刷新 / refresh", ...models];

            // Look for custom dropdown element
            if (modelWidget.input && modelWidget.input.parentNode) {
              const dropdown =
                modelWidget.input.parentNode.querySelector("select");
              if (dropdown) {
                // Update dropdown options
                dropdown.innerHTML = "";
                options.forEach((option) => {
                  const optionElement = document.createElement("option");
                  optionElement.value = option;
                  optionElement.textContent = option;
                  dropdown.appendChild(optionElement);
                });

                // Enhanced selection logic
                const currentValue = modelWidget.value || "刷新 / refresh";
                let selectedValue = currentValue;

                if (autoSelectFirst && models.length > 0) {
                  // Auto-select first model when server changes
                  selectedValue = models[0];
                  console.log(`Auto-selecting first model: ${selectedValue}`);
                } else if (options.includes(currentValue)) {
                  // Preserve current selection if it's still valid
                  selectedValue = currentValue;
                } else if (models.length > 0) {
                  // Select first available model if current is invalid
                  selectedValue = models[0];
                  console.log(
                    `Current selection invalid, selecting: ${selectedValue}`
                  );
                } else {
                  // No models available, keep refresh
                  selectedValue = "刷新 / refresh";
                }

                dropdown.value = selectedValue;
                modelWidget.value = selectedValue;

                // Trigger callback if value changed and it's not refresh
                if (
                  selectedValue !== currentValue &&
                  selectedValue !== "刷新 / refresh" &&
                  modelWidget.callback
                ) {
                  setTimeout(() => {
                    modelWidget.callback(selectedValue);
                  }, 100);
                }

                console.log(
                  `Updated dropdown for node ${node.id} with ${models.length} models, selected: ${selectedValue}`
                );
              }
            }
          }
        }
      });
    }
  },

  getCachedModels(serverName) {
    return this.modelsCache.get(serverName) || [];
  },
};

// Register the extension
app.registerExtension({
  name: "Siberia.Ollama",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    // Check if this is our Ollama Connector node
    if (nodeData.name === "SiberiaOllamaConnector") {
      // Override the onNodeCreated method
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const result = onNodeCreated
          ? onNodeCreated.apply(this, arguments)
          : undefined;

        // Wait for widgets to be created
        setTimeout(() => {
          try {
            // Find the model widget and server widget
            const modelWidget = this.widgets.find((w) => w.name === "model");
            const serverWidget = this.widgets.find(
              (w) => w.name === "server_name"
            );

            if (modelWidget && serverWidget) {
              console.log(
                "🎯 SiberiaOllamaConnector node created - Converting to COMBO widget"
              );

              // Convert STRING widget to COMBO widget
              const originalCallback = modelWidget.callback;
              
              // Store the widget index
              const widgetIndex = this.widgets.indexOf(modelWidget);
              
              // Remove the old STRING widget
              this.widgets.splice(widgetIndex, 1);
              
              // Create a new COMBO widget
              const comboWidget = this.addWidget(
                "combo",
                "model",
                "刷新 / refresh",
                (value) => {
                  console.log(`✅ Model changed to: ${value}`);
                  if (value === "刷新 / refresh") {
                    console.log("🔄 Refreshing models...");
                    updateModelOptions(serverWidget.value);
                  } else if (originalCallback) {
                    originalCallback.call(comboWidget, value);
                  }
                },
                {
                  values: ["刷新 / refresh", "正在加载... / Loading..."],
                }
              );
              
              // Move the combo widget to the correct position
              if (widgetIndex < this.widgets.length - 1) {
                this.widgets.splice(widgetIndex, 0, this.widgets.pop());
              }
              
              // Update dropdown options function
              const updateDropdownOptions = (options) => {
                console.log("Updating dropdown with options:", options);
                comboWidget.options.values = options;
                
                // Set current value
                const currentValue = comboWidget.value || options[0] || "";
                const newValue = options.includes(currentValue)
                  ? currentValue
                  : options[0] || "";
                
                comboWidget.value = newValue;
                
                console.log(`Set dropdown value to: ${newValue}`);
                console.log(`Dropdown has ${options.length} options`);
                
                // Force node to redraw
                this.setDirtyCanvas(true, true);
              };
              
              const dropdownManager = {
                updateOptions: updateDropdownOptions,
                getValue: () => comboWidget.value,
                setValue: (value) => {
                  if (comboWidget.options.values.includes(value)) {
                    comboWidget.value = value;
                  }
                },
              };

              // Function to update model options
              async function updateModelOptions(serverName) {
                try {
                  const cachedModels =
                    siberiaManager.getCachedModels(serverName);

                  if (cachedModels.length > 0) {
                    // Use cached models
                    const options = ["刷新 / refresh", ...cachedModels];
                    dropdownManager.updateOptions(options);
                    console.log(
                      "Updated dropdown with cached models:",
                      cachedModels.length
                    );
                  } else {
                    // Show loading state
                    dropdownManager.updateOptions([
                      "刷新 / refresh",
                      "正在加载... / Loading...",
                    ]);

                    // Fetch fresh models
                    const models = await siberiaManager.fetchModels(serverName);
                    if (models.length > 0) {
                      const options = ["刷新 / refresh", ...models];
                      dropdownManager.updateOptions(options);

                      // Auto-select first model if current is refresh
                      if (comboWidget.value === "刷新 / refresh") {
                        const firstModel = models[0];
                        dropdownManager.setValue(firstModel);
                      }
                    } else {
                      // Connection failed - show only refresh option
                      dropdownManager.updateOptions(["刷新 / refresh"]);
                      console.log("No models available, showing refresh only");
                    }
                  }
                } catch (error) {
                  console.error("Error updating model options:", error);
                  // Connection error - show only refresh option
                  dropdownManager.updateOptions(["刷新 / refresh"]);
                }
              }

              // Handle server changes - safe callback wrapper
              if (serverWidget.callback) {
                const originalServerCallback = serverWidget.callback;
                serverWidget.callback = function (value) {
                  console.log("🌐 Server changed to:", value);

                  try {
                    // Update models for new server
                    updateModelOptions(value);

                    // Call original callback
                    originalServerCallback.call(this, value);
                  } catch (error) {
                    console.error("Error in server callback:", error);
                  }
                };
              }

              // Initial load with longer delay
              setTimeout(() => {
                console.log("🚀 Initial model load...");
                updateModelOptions(serverWidget.value);
              }, 2000);
            } else {
              console.warn("⚠️ Could not find required widgets");
            }
          } catch (error) {
            console.error("Error in SiberiaOllamaConnector setup:", error);
          }
        }, 500);

        return result;
      };
    }
  },
});
