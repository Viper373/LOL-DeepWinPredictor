$(document).ready(function () {
    // 更新当前时间
    function updateTime() {
        const now = new Date();
        const formattedTime = now.toLocaleString();
        $('#current-time').text(formattedTime);
    }

    // 每秒更新一次时间
    setInterval(updateTime, 1000);
    updateTime(); // 页面加载时立即更新一次时间

    let hero_list = [];
    let hero_win_rate = {};
    let team_list = [];
    let autocompleteSource = [];

    const loadData = (url) => {
        return $.getJSON(url).fail((jqXHR, textStatus, errorThrown) => {
            console.error(`加载数据失败: ${textStatus}, ${errorThrown}`);
        });
    };

    const triggerAutocomplete = debounce(function (inputElement) {
        if (inputElement && inputElement.val()) {
            const query = inputElement.val();
            if (query.length >= 1 && !inputElement.data('autocompleting')) {
                const dataType = inputElement.hasClass('hero-input') ? 'hero' : 'team';
                autocompleteSource = generateAutocompleteSource(dataType, query);
                inputElement.autocomplete("option", "source", autocompleteSource).autocomplete("search", query);
            }
        }
    }, 300);

    $(".hero-input, .team-name-input").on("input", function () {
        const $this = $(this);
        if ($this.val()) {
            triggerAutocomplete($this);
        }
        fetchDataAndUpdateChart(); // 实时更新图表
    });

    Promise.all([
        loadData("/query_hero"),
        loadData("/query_win_rate"),
        loadData("/query_team")
    ]).then(([heroes, winRates, teams]) => {
        hero_list = heroes;
        hero_win_rate = winRates.data;
        team_list = teams;  // 这里确保正确地访问 team 数据
        initAutocomplete();
    }).catch(error => {
        console.error('加载数据失败:', error);
    });

    function initAutocomplete() {
        $(".hero-input, .team-name-input").each(function () {
            const $this = $(this);
            const dataType = $this.hasClass('hero-input') ? 'hero' : 'team';

            $this.autocomplete({
                source: function (request, response) {
                    const query = request.term;
                    if (query.length >= 1) {
                        const source = generateAutocompleteSource(dataType, query);
                        response(source);
                    }
                },
                select: function (event, ui) {
                    $this.val(ui.item.label);
                    if ($this.hasClass('hero-input')) {
                        $this.data('hero-id', ui.item.id);
                        $this.attr('value', ui.item.id); // 添加value属性
                    } else {
                        $this.data('team-id', ui.item.id);
                    }
                    // 显示logo在输入框内部的尾部
                    $this.css('background-image', `url(${ui.item.logo})`);
                    $this.css('background-repeat', 'no-repeat');
                    $this.css('background-position', 'right 10px center');
                    $this.css('background-size', '30px 30px');
                    fetchDataAndUpdateChart(); // 实时更新图表
                    return false;
                },
                open: function () {
                    $this.data('autocompleting', true);
                },
                close: function () {
                    $this.data('autocompleting', false);
                }
            }).autocomplete("instance")._renderItem = function (ul, item) {
                return $("<li>")
                    .append(`<div style="display: flex; justify-content: space-between; align-items: center;">${item.label}<img src="${item.logo}" alt="logo" style="width:30px; height:30px; margin-left:10px;"></div>`)
                    .appendTo(ul);
            };
        });
    }

    function generateAutocompleteSource(dataType, query) {
        let source = [];
        try {
            if (dataType === 'hero') {
                const fuse = new Fuse(hero_list, {
                    keys: ['name', 'keywords'],
                    threshold: 0.3
                });
                source = fuse.search(query).map(result => ({
                    label: result.item.name,
                    value: result.item.name,
                    id: result.item.heroId,
                    logo: result.item.heroLogo
                }));
            } else if (dataType === 'team') {
                const teamsArray = Object.values(team_list);
                const fuse = new Fuse(teamsArray, {
                    keys: ['TeamName', 'TeamShortName'],
                    threshold: 0.3
                });
                source = fuse.search(query).map(result => ({
                    label: result.item.TeamName,
                    value: result.item.TeamName,
                    id: result.item.TeamId,
                    logo: result.item.TeamLogo
                }));
            }
        } catch (error) {
            console.error('生成自动补全数据源时出错:', error);
        }
        return source;
    }

    function debounce(func, wait) {
        let timeout;
        return function () {
            clearTimeout(timeout);
            timeout = setTimeout(func, wait);
        };
    }

    // 初始化ECharts图表
    let myChart = echarts.init(document.getElementById('win-rate-chart'));

    function initChart() {
        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                },
                formatter: function (params) {
                    var result = params[0].name + '<br/>';
                    params.forEach(function (item) {
                        result += item.marker + " " + item.seriesName + ": " + (item.value).toFixed(2) + "%<br/>";
                    });
                    return result;
                }
            },
            xAxis: {
                type: 'category',
                data: ['TOP', 'JUN', 'MID', 'ADC', 'SUP']
            },
            yAxis: {
                type: 'value',
                min: 0,
                max: 70,
                axisLabel: {
                    formatter: '{value} %'
                },
                splitLine: {
                    show: false
                }
            },
            series: [
                {
                    name: 'A队',
                    type: 'bar',
                    data: [],
                    itemStyle: {
                        color: '#5470C6'
                    },
                    label: {
                        show: true,
                        position: 'top',
                        formatter: function (params) {
                            return params.value.toFixed(2) + "%"; // 确保显示小数点后两位
                        }
                    }
                },
                {
                    name: 'B队',
                    type: 'bar',
                    data: [],
                    itemStyle: {
                        color: '#91CC75'
                    },
                    label: {
                        show: true,
                        position: 'top',
                        formatter: function (params) {
                            return params.value.toFixed(2) + "%"; // 确保显示小数点后两位
                        }
                    }
                }
            ]
        };
        myChart.setOption(option);
    }

    initChart();

    function updateChart(data) {
        // 获取左队和右队输入框中选择的英雄ID
        const leftHeroIds = $('#left-team .hero-input').map(function () {
            return $(this).data('hero-id') || 0; // 默认为0
        }).get();

        const rightHeroIds = $('#right-team .hero-input').map(function () {
            return $(this).data('hero-id') || 0; // 默认为0
        }).get();

        const leftWinRates = [];
        const rightWinRates = [];
        const positions = ['top', 'jun', 'mid', 'adc', 'sup'];

        leftHeroIds.forEach(function (heroId, index) {
            if (heroId && data[heroId]) {
                const position = positions[index % 5];
                leftWinRates.push(data[heroId][position] * 100).toFixed(2);  // 将胜率转换为百分比并四舍五入到小数后两位
            } else {
                leftWinRates.push(0);
            }
        });

        rightHeroIds.forEach(function (heroId, index) {
            if (heroId && data[heroId]) {
                const position = positions[index % 5];
                rightWinRates.push(data[heroId][position] * 100).toFixed(2);  // 将胜率转换为百分比并四舍五入到小数后两位
            } else {
                rightWinRates.push(0);
            }
        });

        myChart.setOption({
            series: [
                {
                    name: 'A队',
                    data: leftWinRates.map(rate => parseFloat(rate)) // 将字符串转换为浮点数
                },
                {
                    name: 'B队',
                    data: rightWinRates.map(rate => parseFloat(rate)) // 将字符串转换为浮点数
                }
            ]
        });
    }

    // 获取数据并更新图表
    function fetchDataAndUpdateChart() {
        $.getJSON('/get_echarts_data', function (data) {
            updateChart(data);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.error(`加载数据失败: ${textStatus}, ${errorThrown}`);
        });
    }

    // 初始化加载数据并绘制图表
    fetchDataAndUpdateChart();

    // 英雄输入框自动补全选择时触发数据加载和图表更新
    $(".hero-input").autocomplete({
        source: function (request, response) {
            const query = request.term;
            if (query.length >= 1) {
                const source = generateAutocompleteSource('hero', query);
                response(source);
            }
        },
        select: function (event, ui) {
            $(this).val(ui.item.label);
            $(this).data('hero-id', ui.item.id);
            $(this).attr('value', ui.item.id); // 添加value属性
            fetchDataAndUpdateChart(); // 获取数据并更新图表
            return false;
        },
        open: function () {
            $(this).data('autocompleting', true);
        },
        close: function () {
            $(this).data('autocompleting', false);
        }
    }).autocomplete("instance")._renderItem = function (ul, item) {
        return $("<li>")
            .append(`<div style="display: flex; justify-content: space-between; align-items: center;">${item.label}<img src="${item.logo}" alt="logo" style="width:30px; height:30px; margin-left:10px;"></div>`)
            .appendTo(ul);
    };

    // 预测按钮点击事件
    $("#predict-btn").on("click", function () {
        const leftTeamData = getTeamData("#left-team", $("#left-team-name").data('team-id'), 'A');
        const rightTeamData = getTeamData("#right-team", $("#right-team-name").data('team-id'), 'B');
        if (leftTeamData.length < 5 || rightTeamData.length < 5) {
            alert("请确保每队选择五个英雄");
            return;
        }

        const requestData = {
            left_team: leftTeamData,
            right_team: rightTeamData
        };

        $.ajax({
            type: "POST",
            url: "/predict",
            contentType: "application/json",
            data: JSON.stringify(requestData),
            success: function (response) {
                $("#A-win-rate").text(response.A_win.toFixed(2) + "%");
                $("#B-win-rate").text(response.B_win.toFixed(2) + "%");
                $("#winning-team-name").text(response.winning_team.name);
                $("#winning-team-logo").attr("src", response.winning_team.logo).show();
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error(`预测请求失败: ${textStatus}, ${errorThrown}`);
                alert("预测请求失败，请稍后重试");
            }
        });
    });

    // 获取队伍数据，包括英雄的胜率、hero_id和位置
    function getTeamData(teamSelector, teamId, teamPrefix) {
        const teamData = {[`team${teamPrefix}id`]: Number(teamId)};
        $(teamSelector + " .hero-input").each(function (index) {
            const role = $(this).data("role");
            const roleIndex = getRoleIndex(role); // 获取角色的整数索引
            const heroName = $(this).val().trim().toLowerCase();
            if (heroName) {
                const hero = hero_list.find(h =>
                    h.name.toLowerCase() === heroName ||
                    h.keywords.split(',').map(k => k.toLowerCase()).includes(heroName)
                );
                if (hero) {
                    const heroId = hero.heroId;
                    const winRate = getHeroWinRate(heroId, role); // 获取英雄在该分路的胜率
                    teamData[`${teamPrefix}${index + 1}playerLocation`] = roleIndex;
                    teamData[`${teamPrefix}${index + 1}heroId`] = Number(heroId);
                    teamData[`${teamPrefix}${index + 1}heroWinRate`] = winRate;
                } else {
                    console.error(`无法找到英雄: ${heroName}`);
                    teamData[`${teamPrefix}${index + 1}playerLocation`] = roleIndex;
                    teamData[`${teamPrefix}${index + 1}heroId`] = null;
                    teamData[`${teamPrefix}${index + 1}heroWinRate`] = 0.5; // 如果找不到英雄，推入一个默认值
                }
            }
        });
        return teamData;
    }


    // 将角色名称转换为索引
    function getRoleIndex(role) {
        role = role.toUpperCase();
        switch (role) {
            case 'TOP':
                return 0;
            case 'JUNGLE':
            case 'JUN':
                return 1;
            case 'MID':
            case 'MIDDLE':
                return 2;
            case 'ADC':
            case 'BOT':
            case 'BOTTOM':
                return 3;
            case 'SUP':
            case 'SUPPORT':
                return 4;
            default:
                return 99; // 使用99作为默认值，以防止未识别的角色名称
        }
    }
    // 获取英雄在指定分路的胜率
    function getHeroWinRate(heroId, role) {
        const positionMap = {
            0: ['TOP'],
            1: ['JUNGLE', 'JUN'],
            2: ['MID', 'MIDDLE'],
            3: ['ADC', 'BOT', 'BOTTOM'],
            4: ['SUPPORT', 'SUP']
        };

        let positionName;
        for (const [key, values] of Object.entries(positionMap)) {
            if (values.includes(role.toUpperCase())) {
                positionName = values[0]; // 使用标准名称
                break;
            }
        }

        if (!positionName) {
            console.error(`未知的角色位置: ${role}`);
            return 0.5; // 返回默认值
        }

        const heroData = hero_win_rate.find(h => h.champion.id == heroId);
        if (heroData) {
            const positionData = heroData.champion.positions.find(p => p.name.toUpperCase() === positionName.toUpperCase());
            if (positionData) {
                return positionData.stats.win_rate;
            }
        }
        return 0.5; // 如果没有找到对应的胜率，返回0.5
    }

});
