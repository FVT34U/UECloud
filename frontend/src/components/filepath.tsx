import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
  } from "@/components/ui/breadcrumb"
import { randomUUID } from "crypto"
  

interface ContentProps {
    path: string
    updateTable: (name: string) => void
}

const temp =
<>
    <BreadcrumbItem>
        <BreadcrumbLink href="/">Workspaces</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
        <BreadcrumbLink href="/adminsk">Projects</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
        <BreadcrumbPage>adminsk</BreadcrumbPage>
    </BreadcrumbItem>
</>


function Filepath({path, updateTable}: ContentProps) {
    const pathElements = path.split('/').slice(0, -1)

    const makePathLinks = (): string[] => {
        return pathElements.reduce((acc, path, index) => {
            const currentPath = index === 0 ? path : `${acc[index - 1]}/${path}`;
            return [...acc, currentPath];
        }, [] as string[])
    }

    const pathLinks = makePathLinks()

    console.log('pathLinks', pathLinks)

    return(
        <Breadcrumb className="px-10 py-5">
            <BreadcrumbList>
                <BreadcrumbItem key={'Workspace'}>
                    <BreadcrumbLink onClick={() => updateTable('/')}>Workspaces</BreadcrumbLink>
                </BreadcrumbItem>
                {
                    pathElements.map((p, index) => (
                        <BreadcrumbItem key={index}>
                            <BreadcrumbSeparator />
                            <BreadcrumbLink onClick={() => updateTable(pathLinks[index])}>{p}</BreadcrumbLink>
                        </BreadcrumbItem>
                    ))
                }
            </BreadcrumbList>
        </Breadcrumb>
    )
}

export default Filepath