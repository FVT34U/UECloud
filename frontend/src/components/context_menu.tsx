import {
    ContextMenu,
    ContextMenuContent,
    ContextMenuItem,
    ContextMenuTrigger,
  } from "@/components/ui/context-menu"


function TableContextMenu() {
	return (
		<ContextMenu>
			<ContextMenuTrigger className="flex w-96 h-36 items-center justify-center rounded-md border-8 border-dashed text-sm">
			</ContextMenuTrigger>
			<ContextMenuContent>
				<ContextMenuItem>Profile</ContextMenuItem>
				<ContextMenuItem>Billing</ContextMenuItem>
				<ContextMenuItem>Team</ContextMenuItem>
				<ContextMenuItem>Subscription</ContextMenuItem>
			</ContextMenuContent>
		</ContextMenu>
	)
}

export default TableContextMenu
