import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
  } from "@/components/ui/breadcrumb"
  

interface ContentProps {
    path: string[]
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


function Filepath({path}: ContentProps) {
    if (path.length === 0) {
        path = ['Workspaces']
    }

    return(
        <Breadcrumb className="px-10 py-5">
            <BreadcrumbList>
                {
                    path.map(p => (
                        <>
                            <BreadcrumbItem>
                                {p}
                            </BreadcrumbItem>
                            <BreadcrumbSeparator />
                        </>
                    ))
                }
            </BreadcrumbList>
        </Breadcrumb>
    )
}

export default Filepath