import axios from "axios"
import Filepath from "./filepath"
import Filetable from "./filetable"
import { useEffect, useState } from "react"
import { error } from "console"


interface Entity {
    _id: string
    name: string
    type: string
    owner: string
    parent: string
    path: string
}

export type EntityList = Entity[];


async function fetchFiles(path: string): Promise<EntityList> {
    let entities: EntityList = [];
    let url = `https://127.0.0.1:8000/api/workspace/${path}`;

    await axios.get(url, {
        withCredentials: true,
    })
    .then(resp => {
        entities = resp.data['entity_list'];
    })
    .catch(error => {
        return [];
    })

    return entities;
};


function Content() {
    const [entityList, setEntityList] = useState<EntityList>([]);
    const [path, setPath] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            const data = await fetchFiles('/');
            setEntityList(data);
            try {
                setPath(data[0].path);
            }
            catch {} // TODO: сделать так, чтобы название папки отображалось в любом случае, даже если там пусто
        }

        fetchData();
    }, []);

    const updateTable = async (name: string) => {
        const data = await fetchFiles(name);
        setEntityList(data);
        try {
            setPath(data[0].path);
        }
        catch {} // TODO: сделать так, чтобы название папки отображалось в любом случае, даже если там пусто
    }

    return(
        <>
        <Filepath path={path} updateTable={updateTable}></Filepath>
        <Filetable entityList={entityList} updateTable={updateTable}></Filetable>
        </>
    )
}

export default Content