let chart;
let municipalities = [];
let kpis = [];

//Runs necessary functions on load
document.addEventListener('DOMContentLoaded', async () => {
    await fetchMunicipalities();
    await fetchKPIs();
    initializeSelect2();
    document.getElementById('updateButton').addEventListener('click', updateChart);
});

//Fetches a list of all municipalities in the database
async function fetchMunicipalities() {
    const response = await fetch('/municipalities/');
    municipalities = await response.json();
}

//Fetches a list of all KPIs in the database
async function fetchKPIs() {
    const response = await fetch('/kpis/');
    kpis = await response.json();
    return kpis.map(kpi => ({
        kpi_id: kpi.kpi_id,
        kpi_name: kpi.name,
        kpi_description: kpi.description
    }));
}

//Boots up the multi-select textboxes
function initializeSelect2() {

    $('#kpiSelect').select2({
        placeholder: 'Välj ett nyckeltal',
        allowClear: true,
        data: kpis.map(kpi => ({ id: kpi.kpi_id, text: kpi.name }))
    });

    $('#municipalitySelect').select2({
        placeholder: 'Välj huvudmän att jämföra',
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

//Big function that creates the graph/chart plot with all data 
async function updateChart() {
    console.log('Updating chart...');
    const selectedKPIId = $('#kpiSelect').val();
    const selectedMunicipalities = $('#municipalitySelect').val();
    console.log('Selected KPI ID:', selectedKPIId);
    console.log('Selected municipalities:', selectedMunicipalities);

    if (!selectedMunicipalities || selectedMunicipalities.length === 0) {
        alert('Please select at least one municipality.');
        return;
    }

    const selectedKPIData = kpis.find(kpi => kpi.kpi_id === selectedKPIId);

    const tableContainer = document.getElementById('tableContainer');
    tableContainer.innerHTML = '';
    const datasets = [];

    //some print outs

    for (const municipalityId of selectedMunicipalities) {
        try {
            await fetchMunicipalityData(selectedKPIId, municipalityId);
            const data = await fetchStructuredMunicipalityData(selectedKPIId, municipalityId);
            // Find the municipality data for the selected KPI
            const color = getRandomColor();
            datasets.push({
                label: data.municipality_name,
                //This f-ing sucked to map out
                data: data.values.flatMap(item => item.value.values.flatMap(item2 => item2.values.flatMap( item3 =>
                    ({ x: item2.period, y: item3.value })))),
                borderColor: color,
                backgroundColor: color + '20',
                fill: false
            });
        } catch (error) {
            console.error(`Error fetching data for municipality ${municipalityId}:`, error);
        }
    }

    // Set the KPI name and description
    const kpiNameElement = document.getElementById('kpiName');
    const kpiDescriptionElement = document.getElementById('kpiDescription');
    kpiNameElement.textContent = selectedKPIData.name;
    kpiDescriptionElement.textContent = selectedKPIData.description;

    // Create and append the comparison table
    const comparisonTable = createComparisonTable(datasets);
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
                            text: 'År'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Värde'
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
    return number.toLocaleString('sv-SE', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
    });
}


// Downloads the data from Kolada
async function fetchMunicipalityData(kpiId, municipalityId) {
    await fetch(`/fetch_municipality_data?kpi_id=${kpiId}&municipality_id=${municipalityId}`);
}

//Prepares and formats the data from Kolada
async function fetchStructuredMunicipalityData(kpiId, municipalityId) {
    const response = await fetch(`/structured_municipality_data/${municipalityId}?kpi_id=${kpiId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

//Does what it says
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

//...
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

//Lays the foundation for the compirson table 
function createComparisonTable(datasets) {
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    // Create the table header
    const headerRow = document.createElement('tr');
    const headerCells = [''];
    headerCells.push(...new Set(datasets.map(dataset => dataset.label)));
    headerCells.forEach(cell => {
        const th = document.createElement('th');
        th.textContent = cell;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Create the table body
    const allYears = new Set();
    for (const dataset of datasets) {
        dataset.data.forEach(item => {
            allYears.add(item.x);
        });
    }

    for (const year of Array.from(allYears).sort().reverse()) {
        const row = document.createElement('tr');
        const yearCell = document.createElement('td');
        yearCell.textContent = year;
        row.appendChild(yearCell);

        for (const dataset of datasets) {
            const value = dataset.data.find(item => item.x === year)?.y;
            const cell = document.createElement('td');
            cell.textContent = value !== undefined ? formatNumberEuropean(value) : '';
            row.appendChild(cell);
        }

        tbody.appendChild(row);
    }

    table.appendChild(thead);
    table.appendChild(tbody);
    return table;
}