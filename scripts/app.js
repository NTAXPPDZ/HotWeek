/**
 * GitHub热榜网页交互脚本
 *
 * 功能：处理数据加载、筛选、搜索、分页等交互逻辑
 * 作者：Auto-generated
 * 版本：1.0.0
 */

class GitHubTrendingApp {
  constructor() {
    this.data = null;
    this.filteredData = [];
    this.currentPage = 1;
    this.itemsPerPage = 12;
    this.currentLanguage = "";
    this.currentSearch = "";
    this.currentSort = "stars";

    this.init();
  }

  /**
   * 初始化应用
   */
  init() {
    // 等待DOM完全加载
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => {
        this.bindEvents();
        this.loadData();
      });
    } else {
      this.bindEvents();
      this.loadData();
    }
  }

  /**
   * 绑定事件监听器
   */
  bindEvents() {
    // 搜索功能
    const searchInput = document.getElementById("searchInput");
    searchInput.addEventListener(
      "input",
      this.debounce(() => {
        this.currentSearch = searchInput.value.trim();
        this.filterAndRender();
      }, 300)
    );

    // 语言筛选
    const languageFilter = document.getElementById("languageFilter");
    languageFilter.addEventListener("change", (e) => {
      this.currentLanguage = e.target.value;
      this.filterAndRender();
    });

    // 排序功能
    const sortFilter = document.getElementById("sortFilter");
    sortFilter.addEventListener("change", (e) => {
      this.currentSort = e.target.value;
      this.sortAndRender();
    });

    // 刷新按钮
    const refreshBtn = document.getElementById("refreshBtn");
    refreshBtn.addEventListener("click", () => {
      this.loadData(true);
    });

    // 重试按钮
    const retryBtn = document.getElementById("retryBtn");
    retryBtn.addEventListener("click", () => {
      this.loadData(true);
    });

    // 分页按钮
    const prevPageBtn = document.getElementById("prevPage");
    const nextPageBtn = document.getElementById("nextPage");

    if (prevPageBtn) {
      prevPageBtn.addEventListener("click", () => {
        this.previousPage();
      });
    }

    if (nextPageBtn) {
      nextPageBtn.addEventListener("click", () => {
        this.nextPage();
      });
    }

    // 关于模态框
    const aboutLink = document.getElementById("aboutLink");
    const closeModalBtn = document.getElementById("closeModal");
    const aboutModal = document.getElementById("aboutModal");

    if (aboutLink) {
      aboutLink.addEventListener("click", (e) => {
        e.preventDefault();
        this.showAboutModal();
      });
    }

    if (closeModalBtn) {
      closeModalBtn.addEventListener("click", () => {
        this.hideAboutModal();
      });
    }

    if (aboutModal) {
      // 点击模态框背景关闭
      aboutModal.addEventListener("click", (e) => {
        if (e.target.id === "aboutModal") {
          this.hideAboutModal();
        }
      });
    }

    // ESC键关闭模态框
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.hideAboutModal();
      }
    });
  }

  /**
   * 防抖函数
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * 加载数据
   */
  async loadData(forceRefresh = false) {
    this.showLoadingState();

    try {
      // 尝试加载处理后的数据文件
      const timestamp = forceRefresh ? `?t=${Date.now()}` : "";
      let response = await fetch(`data/processed_trending.json${timestamp}`);

      // 如果处理后的数据不存在，尝试加载原始数据
      if (!response.ok) {
        console.warn("处理后的数据文件不存在，尝试加载原始数据...");
        response = await fetch(`data/trending.json${timestamp}`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      const rawData = await response.json();

      // 处理数据格式兼容性
      this.data = this.processDataFormat(rawData);
      this.hideErrorState();
      this.render();
    } catch (error) {
      console.error("数据加载失败:", error);
      this.showErrorState();
    }
  }

  /**
   * 处理数据格式兼容性
   */
  processDataFormat(rawData) {
    // 检查数据格式
    if (rawData.metadata && rawData.repositories) {
      // 已经是处理后的格式
      return rawData;
    } else if (Array.isArray(rawData)) {
      // 原始API返回的数组格式
      return {
        metadata: {
          last_updated: new Date().toISOString(),
          count: rawData.length,
          source: "GitHub Trending API",
        },
        repositories: rawData,
      };
    } else {
      // 未知格式，返回空数据
      console.warn("未知的数据格式，使用空数据");
      return {
        metadata: {
          last_updated: new Date().toISOString(),
          count: 0,
          source: "Unknown",
        },
        repositories: [],
      };
    }
  }

  /**
   * 筛选和渲染数据
   */
  filterAndRender() {
    this.currentPage = 1;
    this.filterData();
    this.render();
  }

  /**
   * 排序和渲染数据
   */
  sortAndRender() {
    this.sortData();
    this.renderProjects();
  }

  /**
   * 筛选数据
   */
  filterData() {
    if (!this.data) return;

    this.filteredData = this.data.repositories.filter((repo) => {
      // 语言筛选
      if (this.currentLanguage && repo.language !== this.currentLanguage) {
        return false;
      }

      // 搜索筛选
      if (this.currentSearch) {
        const searchTerm = this.currentSearch.toLowerCase();
        const searchableText = [repo.full_name, repo.description, repo.language]
          .join(" ")
          .toLowerCase();

        return searchableText.includes(searchTerm);
      }

      return true;
    });

    this.sortData();
  }

  /**
   * 排序数据
   */
  sortData() {
    if (!this.filteredData.length) return;

    this.filteredData.sort((a, b) => {
      switch (this.currentSort) {
        case "stars":
          return b.stars - a.stars;
        case "trending":
          return b.current_period_stars - a.current_period_stars;
        case "forks":
          return b.forks - a.forks;
        case "name":
          return a.full_name.localeCompare(b.full_name);
        default:
          return b.stars - a.stars;
      }
    });
  }

  /**
   * 渲染完整页面
   */
  render() {
    if (!this.data) return;

    this.filterData();
    this.updateStats();
    this.updateLanguageFilter();
    this.renderProjects();
    this.updatePagination();
    this.updateLastUpdated();

    this.hideLoadingState();
  }

  /**
   * 更新统计信息
   */
  updateStats() {
    const totalProjects = this.filteredData.length;
    const totalStars = this.filteredData.reduce(
      (sum, repo) => sum + repo.stars,
      0
    );
    const languageCount = new Set(
      this.filteredData.map((repo) => repo.language)
    ).size;
    const trendingStars = this.filteredData.reduce(
      (sum, repo) => sum + repo.current_period_stars,
      0
    );

    document.getElementById("totalProjects").textContent =
      this.formatNumber(totalProjects);
    document.getElementById("totalStars").textContent =
      this.formatNumber(totalStars);
    document.getElementById("languageCount").textContent = languageCount;
    document.getElementById("trendingStars").textContent =
      this.formatNumber(trendingStars);

    document.getElementById("totalCount").textContent = `${this.formatNumber(
      totalProjects
    )} 个项目`;

    // 显示/隐藏统计区域
    const statsSection = document.getElementById("statsSection");
    statsSection.style.display = totalProjects > 0 ? "block" : "none";
  }

  /**
   * 更新语言筛选器选项
   */
  updateLanguageFilter() {
    const languageFilter = document.getElementById("languageFilter");
    const languages = this.data.languages || [];

    // 清空现有选项（保留"所有语言"）
    while (languageFilter.children.length > 1) {
      languageFilter.removeChild(languageFilter.lastChild);
    }

    // 添加语言选项
    languages.forEach((language) => {
      const option = document.createElement("option");
      option.value = language;
      option.textContent = language;
      languageFilter.appendChild(option);
    });
  }

  /**
   * 渲染项目卡片
   */
  renderProjects() {
    const projectsGrid = document.getElementById("projectsGrid");
    const emptyState = document.getElementById("emptyState");

    if (this.filteredData.length === 0) {
      projectsGrid.style.display = "none";
      emptyState.style.display = "block";
      return;
    }

    emptyState.style.display = "none";
    projectsGrid.style.display = "grid";

    // 计算分页数据
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    const pageData = this.filteredData.slice(startIndex, endIndex);

    // 生成项目卡片HTML
    projectsGrid.innerHTML = pageData
      .map((repo) => this.createProjectCard(repo))
      .join("");
  }

  /**
   * 创建项目卡片HTML
   */
  createProjectCard(repo) {
    return `
            <article class="project-card" onclick="window.open('${
              repo.url
            }', '_blank')">
                <div class="project-header">
                    <div class="project-title">
                        <h3 class="project-name">${this.escapeHtml(
                          repo.name
                        )}</h3>
                        <div class="project-author">by ${this.escapeHtml(
                          repo.author
                        )}</div>
                    </div>
                    <div class="project-stats">
                        <div class="stat" title="星标数">
                            <i class="fas fa-star"></i>
                            ${repo.stars_text}
                        </div>
                        ${
                          repo.current_period_stars > 0
                            ? `
                            <div class="stat trending" title="本周新增星标">
                                <i class="fas fa-chart-line"></i>
                                +${repo.trending_stars_text}
                            </div>
                        `
                            : ""
                        }
                    </div>
                </div>
                
                ${
                  repo.description
                    ? `
                    <p class="project-description">${this.escapeHtml(
                      repo.description
                    )}</p>
                `
                    : ""
                }
                
                <div class="project-footer">
                    <div class="project-language">
                        <span class="language-color" style="background-color: ${
                          repo.language_color
                        }"></span>
                        <span>${this.escapeHtml(repo.language)}</span>
                    </div>
                    <a href="${
                      repo.url
                    }" class="project-link" onclick="event.stopPropagation()" 
                       target="_blank" rel="noopener noreferrer">
                        查看项目 <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </article>
        `;
  }

  /**
   * 更新分页控件
   */
  updatePagination() {
    const pagination = document.getElementById("pagination");
    const prevBtn = document.getElementById("prevPage");
    const nextBtn = document.getElementById("nextPage");
    const pageInfo = document.getElementById("pageInfo");

    const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);

    if (totalPages <= 1) {
      pagination.style.display = "none";
      return;
    }

    pagination.style.display = "flex";
    prevBtn.disabled = this.currentPage <= 1;
    nextBtn.disabled = this.currentPage >= totalPages;

    pageInfo.textContent = `第 ${this.currentPage} 页，共 ${totalPages} 页`;
  }

  /**
   * 上一页
   */
  previousPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.renderProjects();
      this.updatePagination();
      this.scrollToTop();
    }
  }

  /**
   * 下一页
   */
  nextPage() {
    const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
    if (this.currentPage < totalPages) {
      this.currentPage++;
      this.renderProjects();
      this.updatePagination();
      this.scrollToTop();
    }
  }

  /**
   * 滚动到顶部
   */
  scrollToTop() {
    window.scrollTo({
      top: document.getElementById("projectsGrid").offsetTop - 100,
      behavior: "smooth",
    });
  }

  /**
   * 更新最后更新时间
   */
  updateLastUpdated() {
    const updateTimeElement = document.getElementById("updateTime");
    if (this.data && this.data.metadata && this.data.metadata.last_updated) {
      const lastUpdated = new Date(this.data.metadata.last_updated);
      updateTimeElement.textContent = `最后更新: ${lastUpdated.toLocaleString(
        "zh-CN"
      )}`;
    }
  }

  /**
   * 显示关于模态框
   */
  showAboutModal() {
    document.getElementById("aboutModal").style.display = "flex";
    document.body.style.overflow = "hidden";
  }

  /**
   * 隐藏关于模态框
   */
  hideAboutModal() {
    document.getElementById("aboutModal").style.display = "none";
    document.body.style.overflow = "auto";
  }

  /**
   * 显示加载状态
   */
  showLoadingState() {
    document.getElementById("loadingState").style.display = "block";
    document.getElementById("errorState").style.display = "none";
    document.getElementById("projectsGrid").style.display = "none";
    document.getElementById("statsSection").style.display = "none";
    document.getElementById("pagination").style.display = "none";
  }

  /**
   * 隐藏加载状态
   */
  hideLoadingState() {
    document.getElementById("loadingState").style.display = "none";
  }

  /**
   * 显示错误状态
   */
  showErrorState() {
    document.getElementById("loadingState").style.display = "none";
    document.getElementById("errorState").style.display = "block";
  }

  /**
   * 隐藏错误状态
   */
  hideErrorState() {
    document.getElementById("errorState").style.display = "none";
  }

  /**
   * 格式化数字
   */
  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num.toString();
  }

  /**
   * HTML转义
   */
  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// 页面加载完成后初始化应用
document.addEventListener("DOMContentLoaded", () => {
  new GitHubTrendingApp();
});

// 错误处理
window.addEventListener("error", (event) => {
  console.error("JavaScript错误:", event.error);
});

// 未处理的Promise拒绝
window.addEventListener("unhandledrejection", (event) => {
  console.error("未处理的Promise拒绝:", event.reason);
});
