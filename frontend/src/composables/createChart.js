import { ref } from 'vue'

export function useChartData() {
    const loading = ref(false)

    /**
     * Creates settings for a base chart
     * @param {Object} config - Chart config options
     * @returns {Object} - ApexCharts options object
     */
    const createChartOptions = (config = {}) => {
        const {
            chartType = 'area',
            xAxisTitle = '',
            yAxisTitle = '',
            enableZoom = true,
            enableDownload = false,
            strokeWidth = 2,
            strokeCurve = 'straight',
            colors = ['#4c51bf', '#48bb78', '#f56565', '#ed8936'],
            legendPosition = 'top',
            fillType = null,
            fillOpacity = null,
            strokeDashArray = null,
            xAxisFormatter = (val) => {
                val = val | 0
                return '$' + val.toLocaleString()
            },
            yAxisFormatter = (val) => {
                return '$' + val.toLocaleString()
            },
            tooltipXFormatter = (val) => {
                return 'Elected: $' + val.toLocaleString()
            },
            tooltipYFormatter = (val) => {
                return '$' + val.toLocaleString()
            }
        } = config

        return {
            chart: {
                type: chartType,
                toolbar: {
                show: true,
                offsetX: 0,
                offsetY: 0,
                autoSelected: '',
                tools: {
                    download: enableDownload,
                    zoom: enableZoom,
                    zoomin: enableZoom,
                    zoomout: enableZoom,
                    pan: enableZoom,
                    reset: enableZoom,
                },
                reset: 'Reset Zoom',
                },
                animations: {
                enabled: true,
                easing: 'easeout',
                speed: 150,
                animateGradually: {
                    enabled: true,
                    delay: 800,
                },
                dynamicAnimation: {
                    enabled: true,
                    speed: 800,
                },
                },
                zoom: {
                allowMouseWheelZoom: false,
                },
            },
            dataLabels: {
                enabled: false,
            },
            stroke: {
                curve: strokeCurve,
                width: strokeWidth,
                ...(strokeDashArray && { dashArray: strokeDashArray })
            },
            ...(fillType && {
                fill: {
                type: fillType,
                opacity: fillOpacity || [0.35, 1, 1, 1],
                gradient: {
                    shade: 'light',
                    type: 'vertical',
                    shadeIntensity: 0.5,
                    opacityFrom: 0.7,
                    opacityTo: 0.2,
                }
                }
            }),
            grid: {
                padding: {
                bottom: 30,
                },
            },
            xaxis: {
                type: 'numeric',
                labels: {
                formatter: xAxisFormatter,
                },
                title: {
                text: xAxisTitle,
                offsetY: 15
                },
                categories: [],
                tickAmount: 10,
            },
            yaxis: {
                type: 'numeric',
                labels: {
                formatter: yAxisFormatter,
                },
                title: {
                text: yAxisTitle,
                offsetX: -1,
                offsetY: 5,
                style: {
                    fontSize: '14px',
                    fontWeight: 600,
                }
                },
            },
            legend: {
                position: legendPosition,
            },
            colors: colors,
            tooltip: {
                x: {
                show: true,
                formatter: tooltipXFormatter,
                },
                y: {
                formatter: tooltipYFormatter,
                },
                theme: 'dark',
            },
        }
    }

    /**
     * Extracts Data from results for a specified field
     * @param {Array} results - array of result objects
     * @param {String} field - Field name to extract
     * @returns {Array} - Parsed float array
     */
    const extractField = (results, field) => {
    return results.map(result => parseFloat(result[field]))
  }

    /**
     * Extracts Ordinary income for multiple years
     * @param {Array} results - Array of result objects
     * @param {Array} years - Array of year strings
     * @returns {Array} - Array of arrays, one per year
     */
    const extractOrdinaryIncomeByYears = (results, years) => {
        return years.map(year =>
            results.map(result => parseFloat(result.taxable_ordinary_all_years[year]))
        )
    }

    /**
   * Creates a constant threshold array
   * @param {Number} length - Length of array
   * @param {Number} value - Threshold value
   * @returns {Array} - Array filled with threshold value
   */
  const createThresholdArray = (length, value) => {
    return new Array(length).fill(value)
  }

    /**
     * Builds tax bracket series
     * @param {Object} config - Config object
     * @returns {Array} - Series array for chart
     */
    const buildTaxBracketSeries = (config) => {
        const {
            years,
            ordinaryIncomeByYear,
            taxBrackets,
            elected,
            includeBrackets = true
        } = config

        const seriesArray = []

        // Add area charts for each year's ordinary income
        years.forEach((year, index) => {
            seriesArray.push({
                name: `${year} Taxable Ordinary Income`,
                type: 'area',
                data: ordinaryIncomeByYear[index]
            })
        })

        // Add line charts for each bracket in each year
        if (includeBrackets) {
            years.forEach(year => {
                taxBrackets[year].forEach(bracket => {
                seriesArray.push({
                    name: `${year} - ${bracket.rate} Bracket`,
                    type: 'line',
                    data: elected.map(() => bracket.threshold)
                })
            })
        })
        }

        return seriesArray
    }

    /**
     * Builds a template series array
     * @param {Array} seriesConfig - Array of series config objects
     * @returns {Array} - series array for chart
     */
    const buildSimpleSeries = (seriesConfig) => {
        return seriesConfig.map(config => ({
            name: config.name,
            type: config.type || 'line',
            data: config.data
        }))
    }

    /**
     * Updates chart options with new categories
     * @param {Object} chartOptions - existing chart options
     * @param {Array} categories - New categories array
     * @returns {Object} - updated chart options
     */
    const updateChartCategories = (chartOptions, categories) => {
        return {
            ...chartOptions,
            xaxis: {
                ...chartOptions.xaxis,
                categories: categories
            }
        }
    }

    /**
     * Main function to process chart data
     * @param {Object} data - Reponse data
     * @param {Object} config - Processing config
     * @returns {Object} - processed chart data
     */
    const processChartData = (data, config = {}) => {
        try {
            loading.value = true
            
            if (!data || !data.results) {
                return null
            }

            const {
                extractFields = [],
                years = []
            } = config

            const processed = {}

            // Extract specified fields
            extractFields.forEach(field => {
                processed[field] = extractField(data.results, field)
            })
            
            // Extract ordinary income by years
            processed.ordinaryIncomeByYear = extractOrdinaryIncomeByYears(data.results, years)

            return processed
        } catch (error) {
            console.error('Error processing chart data', error)
            return null
        } finally {
            loading.value = false
        }
    }

    return {
    loading,
    createChartOptions,
    extractField,
    extractOrdinaryIncomeByYears,
    createThresholdArray,
    buildTaxBracketSeries,
    buildSimpleSeries,
    updateChartCategories,
    processChartData
    }
}