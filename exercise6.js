const axios = require("axios");
const dotenv = require("dotenv");

dotenv.config();
const PORT_BASE_URL = "https://api.getport.io/v1";
const PORT_TOKEN = process.env.PORT_TOKEN;

const getBlueprintEntities = async (identifier) => {
    const response = await axios.get(
        `${PORT_BASE_URL}/blueprints/${identifier}/entities`,
        {
            headers: {
                Authorization: PORT_TOKEN,
            },
        }
    );
    return response.data;
};

let EOLFrameworks = [];
let ActiveFrameworks = [];

const calc = async () => {
    const serviceBlueprint = await getBlueprintEntities("service");
    const frameworkBlueprint = await getBlueprintEntities("framework");

    frameworkBlueprint.entities.forEach(({ identifier, properties }) => {
        properties.state === "Active"
            ? ActiveFrameworks.push(identifier)
            : EOLFrameworks.push(identifier);
    });

    const data = serviceBlueprint.entities.map(({ identifier, relations }) => ({
        serviceEntity: identifier,
        NumberOfEOLPackages: relations.used_frameworks.filter((framework) =>
            EOLFrameworks.includes(framework)
        ).length,
    }));

    console.log(data);

    for (const entity of data) {
        await updateEntity("service", entity.serviceEntity, {
            properties: {
                number_of_eol_packages: entity.NumberOfEOLPackages,
            },
        });
    }
};

const updateEntity = async (blueprintIdentifier, entityIdentifier, data) => {
    try {
        const response = await axios.patch(
            `${PORT_BASE_URL}/blueprints/${blueprintIdentifier}/entities/${entityIdentifier}`,
            data,
            {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: PORT_TOKEN,
                },
            }
        );
        console.log(JSON.stringify(response.data));
    } catch (error) {
        console.log(error);
    }
};

calc();
