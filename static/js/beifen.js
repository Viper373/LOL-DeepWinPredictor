$(document).ready(function () {
    init();
});

function init() {
    updateTimeEverySecond();
    initializeAutocomplete();
    initializeChart();
    loadDataAndInitialize();
    initializePredictionButton();
}
function updateTimeEverySecond() {
    function updateTime() {
        const now = new Date();
        const formattedTime = now.toLocaleString();
        $('#current-time').text(formattedTime);
    }

    setInterval(updateTime, 1000);
    updateTime();
}
function loadDataAndInitialize() {
    Promise.all([
        loadData("/query_hero"),
        loadData("/query_win_rate"),
        loadData("/query_team")
    ]).then(([heroes, winRates, teams]) => {
        window.hero_list = heroes;
        window.hero_win_rate = winRates.data;
        window.team_list = teams;
        initAutocomplete();
    }).catch(error => {
        console.error('加载数据失败:', error);
    });
}
function loadData(url) {
    return $.getJSON(url).fail((jqXHR, textStatus, errorThrown) => {
        console.error(`加载数据失败: ${textStatus}, ${errorThrown}`);
    });
}
function initializeAutocomplete() {
    $(".hero-input, .team-name-input").on("input", function () {
        const $this = $(this);
        if ($this.val()) {
            triggerAutocomplete($this);
        }
        fetchDataAndUpdateChart();
    });
}
function triggerAutocomplete(inputElement) {
    debounce(function () {
        if (inputElement && inputElement.val()) {
            const query = inputElement.val();
            if (query.length >= 1 && !inputElement.data('autocompleting')) {
                const dataType = inputElement.hasClass('hero-input') ? 'hero' : 'team';
                const autocompleteSource = generateAutocompleteSource(dataType, query);
                inputElement.autocomplete("option", "source", autocompleteSource).autocomplete("search", query);
            }
        }
    }, 300);
}
function generateAutocompleteSource(dataType, query) {
    let source = [];
    try {
        if (dataType === 'hero') {
            const fuse = new Fuse(window.hero_list, {
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
            const teamsArray = Object.values(window.team_list);
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
                    $this.attr('value', ui.item.id);
                } else {
                    $this.data('team-id', ui.item.id);
                }
                $this.css('background-image', `url(${ui.item.logo})`);
                $this.css('background-repeat', 'no-repeat');
                $this.css('background-position', 'right 10px center');
                $this.css('background-size', '30px 30px');
                fetchDataAndUpdateChart();
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
function initializeChart() {
    window.myChart = echarts.init(document.getElementById('win-rate-chart'));
    const option = {
        title: {
            text: '英雄胜率对比图', // 图表标题
            left: 'center', // 标题位置
            top: 20, // 调整标题距顶部的距离，单位为像素
            textStyle: {
                fontSize: 20, // 字体大小
                fontWeight: 'bold', // 字体粗细
                fontFamily: '宋体', // 字体家族
                color: '#333' // 字体颜色
            }
        },
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
            },
            textStyle: {
                fontFamily: 'Times New Roman', // 设置提示框的字体
                fontSize: 14, // 设置提示框的字体大小
                color: '#000' // 设置提示框的字体颜色
            }
        },
        xAxis: {
            type: 'category',
            data: ['TOP', 'JUN', 'MID', 'ADC', 'SUP'],
            axisLabel: {
                textStyle: {
                    fontFamily: 'Cambria Math', // 设置X轴标签的字体
                    fontSize: 17, // 设置X轴标签的字体大小
                    color: '#333' // 设置X轴标签的字体颜色
                }
            }
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 70,
            axisLabel: {
                formatter: '{value} %',
                textStyle: {
                    fontFamily: 'Cambria Math', // 设置Y轴标签的字体
                    fontSize: 15, // 设置Y轴标签的字体大小
                    color: '#333' // 设置Y轴标签的字体颜色
                }
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
                        return params.value.toFixed(2) + "%";
                    },
                    textStyle: {
                        fontFamily: 'Cambria Math', // 设置数据标签的字体
                        fontSize: 14, // 设置数据标签的字体大小
                        color: '#333' // 设置数据标签的字体颜色
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
                        return params.value.toFixed(2) + "%";
                    },
                    textStyle: {
                        fontFamily: 'Cambria Math', // 设置数据标签的字体
                        fontSize: 14, // 设置数据标签的字体大小
                        color: '#333' // 设置数据标签的字体颜色
                    }
                }
            }
        ]
    };
    window.myChart.setOption(option);
}
function updateChart(data) {
    const leftHeroIds = $('#left-team .hero-input').map(function () {
        return $(this).data('hero-id') || 0;
    }).get();

    const rightHeroIds = $('#right-team .hero-input').map(function () {
        return $(this).data('hero-id') || 0;
    }).get();

    const leftWinRates = [];
    const rightWinRates = [];
    const positions = ['top', 'jun', 'mid', 'adc', 'sup'];

    leftHeroIds.forEach(function (heroId, index) {
        if (heroId && data[heroId]) {
            const position = positions[index % 5];
            leftWinRates.push(data[heroId][position] * 100).toFixed(2);
        } else {
            leftWinRates.push(0);
        }
    });

    rightHeroIds.forEach(function (heroId, index) {
        if (heroId && data[heroId]) {
            const position = positions[index % 5];
            rightWinRates.push(data[heroId][position] * 100).toFixed(2);
        } else {
            rightWinRates.push(0);
        }
    });

    window.myChart.setOption({
        series: [
            {
                name: 'A队',
                data: leftWinRates.map(rate => parseFloat(rate))
            },
            {
                name: 'B队',
                data: rightWinRates.map(rate => parseFloat(rate))
            }
        ]
    });
}
function fetchDataAndUpdateChart() {
    $.getJSON('/get_echarts_data', function (data) {
        updateChart(data);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.error(`加载数据失败: ${textStatus}, ${errorThrown}`);
    });
}
function initializePredictionButton() {
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
}
function getTeamData(teamSelector, teamId, teamPrefix) {
    const teamData = {[`team${teamPrefix}id`]: Number(teamId)};
    $(teamSelector + " .hero-input").each(function (index) {
        const role = $(this).data("role");
        const roleIndex = getRoleIndex(role);
        const heroName = $(this).val().trim().toLowerCase();
        if (heroName) {
            const hero = window.hero_list.find(h =>
                h.name.toLowerCase() === heroName ||
                h.keywords.split(',').map(k => k.toLowerCase()).includes(heroName)
            );
            if (hero) {
                const heroId = hero.heroId;
                const winRate = getHeroWinRate(heroId, role);
                teamData[`${teamPrefix}${index + 1}playerLocation`] = roleIndex;
                teamData[`${teamPrefix}${index + 1}heroId`] = Number(heroId);
                teamData[`${teamPrefix}${index + 1}heroWinRate`] = winRate;
            } else {
                console.error(`无法找到英雄: ${heroName}`);
                teamData[`${teamPrefix}${index + 1}playerLocation`] = roleIndex;
                teamData[`${teamPrefix}${index + 1}heroId`] = null;
                teamData[`${teamPrefix}${index + 1}heroWinRate`] = 0.5;
            }
        }
    });
    return teamData;
}
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
            return 99;
    }
}
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
            positionName = values[0];
            break;
        }
    }

    if (!positionName) {
        console.error(`未知的角色位置: ${role}`);
        return 0.5;
    }

    const heroData = window.hero_win_rate.find(h => h.champion.id == heroId);
    if (heroData) {
        const positionData = heroData.champion.positions.find(p => p.name.toUpperCase() === positionName.toUpperCase());
        if (positionData) {
            return positionData.stats.win_rate;
        }
    }
    return 0.5;
}
