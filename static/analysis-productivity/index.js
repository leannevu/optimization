const textColorFiles = ['/static/red.txt', '/static/green.txt', '/static/blue.txt', '/static/purple.txt'];
read_code_text();
parts = []; //array for code text file, later used to display code from Jupter notebook

//Read text file and turn into array that can be displayed on HTML
async function read_code_text() {
    regexDifferentOrders = await read_color_text(textColorFiles);
    combinedRegex = regexDifferentOrders[0];
    alterRegexGreen = regexDifferentOrders[1];

    fetch('/static/code.txt')
        .then(response => response.text())
        .then(text => {
            // Split on the custom separator ===
            parts = text.split(/\r?\n?===\r?\n?/).map((section, index) => {
                section = section.trim(); //trim extra whitespace
                if (index >= 3 && index <= 13) { //Change precedence of regex
                    section = section.replace(alterRegexGreen, (match, green_num, green_not_num, red, blue, purple, purple_symbols) => {
                        //if (green && (match == '60')) return `<span class="red-highlight">${match}</span>`; tried to make exception for one green, but it impacts other match too. so one color is mismatched in this section
                        if (green_num) return `<span class="green-highlight">${match}</span>`;
                        if (green_not_num) return `<span class="green-highlight">${match}</span>`;
                        if (red) return `<span class="red-highlight">${match}</span>`;
                        if (blue) return `<span class="blue-highlight">${match}</span>`;
                        //if (purple) return `<span class="purple-highlight">${match}</span>`;
                        if (purple_symbols) return `<span class="purple-highlight">${match}</span>`;
                        return match;
                    });
                } else {
                    section = section.replace(combinedRegex, (match, red, green, blue, purple, purple_symbols) => {
                        if (red) return `<span class="red-highlight">${match}</span>`;
                        if (green) return `<span class="green-highlight">${match}</span>`;
                        if (blue) return `<span class="blue-highlight">${match}</span>`;
                        if (purple) return `<span class="purple-highlight">${match}</span>`;
                        if (purple_symbols) return `<span class="purple-highlight">${match}</span>`;
                        return match;
                    });
                }
                section = section.replace(/\r?\n\r?\n?/g, '<br>');
                return section;
            });
        });



}

//Read text files and turn into arrays to categorize different colors in regex
async function read_color_text(urls) {
    // Create an array of fetch promises
    const fetchPromises = urls.map(url => fetch(url).then(response => response.text()));

    // Wait until all fetches finish (array of response objects/promises)
    const texts = await Promise.all(fetchPromises);

    // Process each file's text; trim and split
    const processedArrays = texts.map(text =>
        text.split(/\r?\n\r?\n/).map(s => s.trim())
    );

    //create combined regex pattern function for purple highlights with symbols and non symbols
    function separate_symbols(arr) {
        //separate words and symbols
        arrWords = arr.filter(s => /^[a-zA-Z0-9_]+$/.test(s));
        arrSymbols = arr.filter(s => !/^[a-zA-Z0-9_]+$/.test(s));

        //build regex patterns
        wordPattern = `\\b(${arrWords.join("|")})\\b`;
        symbolPattern = `(${arrSymbols.join("|")})`;

        //combine pattern
        fullPattern = [wordPattern, symbolPattern].join("|");
        return fullPattern;
    }


    //regex that will be used by default for all sections, if not changing order of precedence in pattern
    const combinedRegex = new RegExp(
        `(${processedArrays[0].join("|")})` +           // Group 1: red
        `|\\b(${processedArrays[1].join("|")})\\b` +          // Group 2: green
        `|\\b(${processedArrays[2].join("|")})\\b` +          // Group 3: blue
        `|` + separate_symbols(processedArrays[3]),           // Group 4: purple
        "g"
    );

    greenNumbers = processedArrays[1].filter(s => /^[0-9]+$/.test(s));
    greenNotNumbers = processedArrays[1].filter(s => !/^[0-9]+$/.test(s));
    const greenAltRegex = new RegExp(
        `(?<=[\\s\\u00A0\\[,])(${greenNumbers.join('|')})(?=[,\\]'"])` +
        `|\\b(${greenNotNumbers.join("|")})\\b` +
        `|(${processedArrays[0].join("|")})` +          // Group 2: red
        `|\\b(${processedArrays[2].join("|")})\\b` +          // Group 3: blue
        `|` + separate_symbols(processedArrays[3]),           // Group 4: purple
        "g"
    );

    regexDifferentOrders = [combinedRegex, greenAltRegex];
    return regexDifferentOrders;
}

var current_button = [0, 0];
function nextButton() {
    current_code = current_button[0];
    current_result = current_button[1];
    if (current_code <= 14) {
        if (current_code != current_result) {
            getResult(current_result);
            current_button[1]++;
            document.getElementById('output_result_' + current_result).scrollIntoView({ behavior: 'smooth' });
            document.querySelector('#next-button p').innerHTML = 'Current section: <br>' + current_result + ' - result';
        } else {
            printCode(current_code);
            current_button[0]++;
            document.getElementById('output_code_' + current_result).scrollIntoView({ behavior: 'smooth' });
            document.querySelector('#next-button p').innerHTML = 'Current section: <br>' + (current_code)+ ' - code';
        }
    } else {
        current_button[0] = 0;
        current_button[1] = 0;
        document.querySelector('#next-button p').innerHTML('See section 0\'s code');
    }
}

function printCode(section) {
    //get text
    var code = parts[section];

    //display text
    element_id_code = 'output_code_' + section;
    output = document.getElementById(element_id_code);
    output.innerHTML = code;
    //style display
    output.style.marginTop = "15px";
    //output.style.background = '#F5F5F5';
}

function getResult(section) {
    var fetch_section = '/section_' + section;
    fetch(fetch_section)
        .then(response => response.json())
        .then(data => {
            if ([0,1,3].includes(section)) {
                printIOText(section, data.output);
            } else if (section == 2) {
                printSeriesToDict(section, data.output);
            } else if ([4,7,8,9,10,11].includes(section)) {
                printIOImage(section, data.image);
            } else if (section == 5) {
                printToDictRecords(section, data.output);
            } else if (section == 6 || section == 13 || section == 12) {
                printToDictListAndRecords(section, data.columns, data.output);
            }

            //make line between result and code for readibility
            var line_section = 'line' + section;
            document.getElementById(line_section).classList.toggle("line");
        });
}

//Same function as printToDictRecords, but wanted to keep order of column headers intact
function printToDictListAndRecords(section, columns, data) {
    //get output id
    const element_id_result = 'output_result_' + section;
    const output = document.getElementById(element_id_result);
    //display json text w/ series converted using to_dict
    cols = columns;
    table = "<table style='width: 100%; max-width: 50%; table-layout: auto; text-align: left;'><tr>";

    cols.forEach(col => {
        table += `<th>${col}</th>`;
    });
    table += '</tr>'
    data.forEach(row => {
        table += '<tr>';
        cols.forEach(col => {
            table += `<td>${row[col]}</td>`;
        });
        table += '</tr>';
    });
    table += '</table>';
    output.innerHTML = table;
}

//Create table from to_dict(orient=records) object
function printToDictRecords(section, data) {
    //get output id
    const element_id_result = 'output_result_' + section;
    const output = document.getElementById(element_id_result);
    //display json text w/ series converted using to_dict
    cols = Object.keys(data[0]);
    table = "<table style='width: 100%; max-width: 50%; table-layout: auto; text-align: left;'><tr>";

    cols.forEach(col => {
        table += `<th>${col}</th>`;
    });
    table += '</tr>'
    data.forEach(row => {
        table += '<tr>';
        cols.forEach(col => {
            table += `<td>${row[col]}</td>`;
        });
        table += '</tr>';
    });
    table += '</table>';
    output.innerHTML = table;
}

function printIOImage(section, data) {
    //get output id
    const element_id_result = 'output_result_' + section;
    const output = document.getElementById(element_id_result);
    //display json text
    output.innerHTML = `<img src= "${data}" style="max-width: 50%; height: auto; border-radius: 8px;" />`;
}

function printSeriesToDict(section, data) {
    //get output id
    const element_id_result = 'output_result_' + section;
    const output = document.getElementById(element_id_result);
    //display json text w/ series converted using to_dict

    table = "<table><tr><td>Attribute</td><td>Data</td><tr>";
    Object.entries(data).forEach(([key, value]) => {
        table += `<tr><td>${key}</td><td>${value}</td></tr>`;
    });
    output.innerHTML = table;
}

function printIOText(section, text) {
    //get output id
    const element_id_result = 'output_result_' + section;
    const output = document.getElementById(element_id_result);
    //display json text
    output.innerText = text;
}

function uploadFile() {
    let fileInput = document.getElementById('myfile').files[0];
    let formData = new FormData();
    formData.append('file', fileInput);

    fetch('/upload', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            //Table output
            let table_output = document.getElementById('output');
            let table = "";
            table += '<table id="tableid"><tr>'
            data.info.forEach(col => {
                table += `<th>${col}</th>`
            });
            table += '</tr></table>'
            table_output.innerHTML = table;
            document.getElementById('tableid').style.border = "1px solid black";
        });
}

function printCSV() {
    fetch('/print_csv_headers')
        .then(response => response.json())
        .then(data => {
            //Table output
            let table_output = document.getElementById('output');
            let create_table = "<table id='tableid'><tr>";

            data.columns.forEach(col => {
                create_table += `<th>${col}</th>`;
            });
            create_table += '</tr><tr>';

            Object.keys(data.dtypes).forEach(col => {
                create_table += `<td>${data.dtypes[col]}</td>`;
            });
            create_table += "</tr></table>";
            table_output.innerHTML = create_table;
            document.getElementById('tableid').style.border = "1px solid black";
        });
}

function printAsList() {
    fetch('/print_csv_headers')
        .then(response => response.json())
        .then(data => {
            let table_output = document.getElementById('output');
            let create_list = "<ul style='list-style-type:square;'>";
            Object.entries(data.dtypes).forEach(([col, dtype]) => {
                create_list += `<li id='column_name' style='font-weight: bold; font-size: 20px;'>${col}</li>`;
                create_list += `<li id='data_type' style='margin-left: 35px; list-style-type:none;'>${dtype}</li>`
            });
            create_list += '</ul>';
            table_output.innerHTML = create_list;
        });

}

function printFilteredCSV() {
    fetch('/print_filtered_csv')
        .then(response => response.json())
        .then(data => {
            let table_output = document.getElementById('output');
            let create_table = "<table border='1' style='border-collapse: collapse; padding: 8px;'>";
            columns = Object.keys(data.df[0]);
            create_table += "<tr>"
            columns.forEach(col => {
                create_table += `<th>${col}</th>`
            })
            create_table += "</tr>"
            data.df.forEach(row => {
                create_table += '<tr>'
                columns.forEach(col => {
                    create_table += `<td>${row[col]}</td>`
                })
                create_table += '</tr>'
            })
            create_table += '</table>'
            table_output.innerHTML = create_table;
        });
}

