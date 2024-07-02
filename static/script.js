document.getElementById('fetchButton').addEventListener('click', async () => {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = 'Fetching data...';

    try {
        const response = await fetch('/fetch-kolada-data');
        const data = await response.json();
        resultDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (error) {
        resultDiv.innerHTML = `Error: ${error.message}`;
    }
});

let chart;
let municipalities = [];

async function fetchMunicipalities() {
    const response = await fetch('/municipalities/');
    municipalities = await response.json();
}

function initializeSelect2() {
    $('#municipalitySelect').select2({
        placeholder: 'Search for municipalities',
        allowClear: true,
        multiple: true,
        data: municipalities.map(m => ({ id: m.municipality_id, text: m.municipality_name })),
        ajax: {
            delay: 250,
            processResults: function (data, params) {
                params.term = params.term || '';
                return {
                    results: municipalities.filter(m => 
                        m.municipality_name.toLowerCase().includes(params.term.toLowerCase())
                    ).map(m => ({ id: m.municipality_id, text: m.municipality_name }))
                };
            },
            cache: true
        },
        minimumInputLength: 1
    }).on('select2:select', function (e) {
        // Remove any empty selections that might have been added
        const selectedValues = $(this).val() || [];
        const filteredValues = selectedValues.filter(value => value !== '');
        if (filteredValues.length !== selectedValues.length) {
            $(this).val(filteredValues).trigger('change');
        }
    });
}

async function fetchMunicipalityData(municipalityId) {
    const response = await fetch(`/structured_municipality_data/${municipalityId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}
function formatMetadata(metadata) {
    if (!metadata || Object.keys(metadata).length === 0) {
        return '';
    }

    const formattedItems = Object.entries(metadata).map(([key, value]) => {
        const formattedKey = key.replace(/([A-Z])/g, ' $1').toLowerCase();
        const capitalizedKey = formattedKey.charAt(0).toUpperCase() + formattedKey.slice(1);
        return `<strong>${capitalizedKey}:</strong> ${value}`;
    });

    return formattedItems.join('<br>');
}

function createTable(municipalityData) {
    const table = document.createElement('table');
    table.className = 'municipality-table';
    
    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    ['Year', 'Value', 'Additional Information'].forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });

    const tbody = table.createTBody();
    municipalityData.values.forEach(item => {
        const row = tbody.insertRow();
        row.insertCell().textContent = item.year;
        row.insertCell().textContent = item.value !== null ? item.value.toFixed(2) : 'N/A';
        const metadataCell = row.insertCell();
        metadataCell.innerHTML = formatMetadata(item.metadata);
        metadataCell.className = 'metadata-cell';
    });

    return table;
}

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function createComparisonTable(municipalitiesData) {
    const table = document.createElement('table');
    table.className = 'comparison-table';
    
    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    headerRow.insertCell().textContent = 'Year';
    
    // Add municipality names to the header
    municipalitiesData.forEach(data => {
        const th = document.createElement('th');
        th.textContent = data.municipality_name;
        headerRow.appendChild(th);
    });

    const tbody = table.createTBody();
    
    // Get all unique years
    const allYears = new Set();
    municipalitiesData.forEach(data => {
        data.values.forEach(item => allYears.add(item.year));
    });
    const sortedYears = Array.from(allYears).sort((a, b) => b - a); // Sort years descending

    // Create rows for each year
    sortedYears.forEach(year => {
        const row = tbody.insertRow();
        row.insertCell().textContent = year;

        municipalitiesData.forEach(data => {
            const cell = row.insertCell();
            const yearData = data.values.find(item => item.year === year);
            if (yearData) {
                cell.textContent = formatNumberEuropean(yearData.value);
                
                // Add metadata as tooltip
                if (yearData.metadata && Object.keys(yearData.metadata).length > 0) {
                    const tooltip = formatMetadata(yearData.metadata).replace(/<br>/g, '\n');
                    cell.title = tooltip;
                    cell.classList.add('has-tooltip');
                }
            } else {
                cell.textContent = 'N/A';
            }
        });
    });

    return table;
}

async function updateChart() {
    const selectedMunicipalities = $('#municipalitySelect').val();

    if (!selectedMunicipalities || selectedMunicipalities.length === 0) {
        alert('Please select at least one municipality.');
        return;
    }

    const tableContainer = document.getElementById('tableContainer');
    tableContainer.innerHTML = '';

    const datasets = [];
    const municipalitiesData = [];

    for (const municipalityId of selectedMunicipalities) {
        try {
            const data = await fetchMunicipalityData(municipalityId);
            municipalitiesData.push(data);
            const color = getRandomColor();
            
            datasets.push({
                label: data.municipality_name,
                data: data.values.map(item => ({ x: item.year, y: item.value })),
                borderColor: color,
                backgroundColor: color + '20',
                fill: false
            });
        } catch (error) {
            console.error(`Error fetching data for municipality ${municipalityId}:`, error);
        }
    }

    // Create and append the comparison table
    const comparisonTable = createComparisonTable(municipalitiesData);
    tableContainer.appendChild(comparisonTable);

    if (chart) {
        chart.data.datasets = datasets;
        chart.update();
    } else {
        const ctx = document.getElementById('dataChart').getContext('2d');
        chart = new Chart(ctx, {
            type: 'line',
            data: { datasets },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Value'
                        },
                        ticks: {
                            callback: function(value, index, values) {
                                return formatNumberEuropean(value);
                            }
                        }
                    }
                },
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            let label = data.datasets[tooltipItem.datasetIndex].label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += formatNumberEuropean(tooltipItem.yLabel);
                            return label;
                        }
                    }
                }
            }
        });
    }
}

function formatNumberEuropean(number) {
    if (number === null || isNaN(number)) return 'N/A';
    return number.toLocaleString('de-DE', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetchMunicipalities();
    initializeSelect2();
    document.getElementById('updateButton').addEventListener('click', updateChart);
});