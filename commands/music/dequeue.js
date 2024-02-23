const { SlashCommandBuilder } = require('@discordjs/builders')
const { EmbedBuilder } = require('discord.js')
const { useMainPlayer } = require('discord-player')

module.exports = {
    data: new SlashCommandBuilder()
        .setName('dequeue')
        .setDescription('Dequeues the song at the given index')
        .addNumberOption(option =>
            option.setName('number')
                .setDescription('Enter the SL No. of the song to dequeue')
                .setRequired(true)),

    async execute(interaction) {
        const player = useMainPlayer()
        const queue = player.nodes.get(interaction.guildId)

        // check if there are songs in the queue
        if (!queue || !queue.node.isPlaying()) {
            await interaction.reply('There are no songs in the queue to dequeue')
            return
        }

        let numberOption = interaction.options.getNumber('number')

        if (numberOption === null) {
            await interaction.reply('Please enter a valid number')
            return
        }

        numberOption = Math.trunc(numberOption)

        if (numberOption > queue.tracks.data.length || numberOption <= 0) {
            await interaction.reply('Please enter a valid track SL No.')
            return
        }

        const trackToRemove = queue.tracks.data[numberOption - 1]
        queue.removeTrack(trackToRemove)


        // Tell the user the track has been removed
        await interaction.reply({
            embeds: [
                new EmbedBuilder().setDescription(`**Track Removed**\n` +
                    (trackToRemove
                        ? `\`[${trackToRemove.duration}]\` ${trackToRemove.title} - <@${trackToRemove.requestedBy.id}>`
                        : 'None'),
                ).setThumbnail(trackToRemove.thumbnail),
            ],
        })
    },
}
