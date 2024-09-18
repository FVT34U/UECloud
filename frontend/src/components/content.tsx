import axios from "axios"
import Filepath from "./filepath"
import Filetable from "./filetable"
import { useEffect, useState } from "react"
import { blob } from "stream/consumers"
import TableContextMenu from "./context_menu"


interface Entity {
    _id: string
    name: string
    type: string
    owner: string
    parent: string
    path: string
}

interface EntityResponse {
    parent_type: string
    parent_path: string
    entity_list: Entity[]
}

export type EntityList = Entity[];


async function fetchFiles(path: string): Promise<EntityResponse> {
    let entities: Entity[] = [];
    let resp_type = '';
    let resp_path = '';

    let url = `https://127.0.0.1:8000/api/workspace/${path}`;

    await axios.get(url, {
        withCredentials: true,
    })
    .then(resp => {
        entities = resp.data['entity_list'];
        resp_type = resp.data['parent_type'];
        resp_path = resp.data['parent_path'];
    })
    .catch(error => {
        return {};
    })

    return {
        parent_type: resp_type,
        parent_path: resp_path,
        entity_list: entities,
    };
};

async function downloadFile(path: string, type: string) {
    const filename = path.split('/').slice(-1)[0]

    await axios.postForm(
        'https://127.0.0.1:8000/api/download',
        { path: path, type: type },
        { withCredentials: true, responseType: 'blob' },
    )
    .then(resp => {
        const url = window.URL.createObjectURL(new Blob([resp.data]));

        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename); // Имя файла, которое будет сохранено
        document.body.appendChild(link);
        link.click();

        // Очищаем ссылку после скачивания
        link.parentNode?.removeChild(link);
        window.URL.revokeObjectURL(url);
    })
}


async function uploadFile(file: File | undefined, path: string | undefined) {
    await axios.postForm(
        'https://127.0.0.1:8000/api/upload',
        { file: file, path: path, },
        { withCredentials: true, },
    )
    .then(resp => {
        console.log(resp)
    })
}


function Content() {
    const [entityList, setEntityList] = useState<EntityList>([]);
    const [path, setPath] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            const data = await fetchFiles('/');
            setEntityList(data.entity_list);
            try {
                setPath(data.parent_path);
            }
            catch {}
        }

        fetchData();
    }, []);

    const updateTable = async (name: string) => {
        const data = await fetchFiles(name);
        setEntityList(data.entity_list);
        try {
            setPath(data.parent_path);
        }
        catch {
            let nameArray = name.split('/')
            nameArray.push('temp')
            const newName = nameArray.join('/')
            setPath(newName)
        } // TODO: жуткий костыль, но мне пофиг
    }

    const filepathProps = {
        path: path,
        updateTable: updateTable,
    }
    const filetableProps = {
        entityList: entityList,
        path: path,
        updateTable: updateTable,
        downloadFile: downloadFile,
        uploadFile: uploadFile,
    }

    return(
        <>
        <Filepath {...filepathProps}></Filepath>
        <Filetable {...filetableProps}></Filetable>
        </>
    )
}

export default Content